"""Bennett 2025 (Nature, doi 10.1038/s41586-025-09721-5) Supplementary Methods Table 6.

The antibody end of the spread: the same family of methods as the miniprotein
papers, on antibody variable domains, gives 0% to 2% over 96 designs per target
by SPR and 0.01% to 0.2% over 9,000 designs per target by yeast display.

Table 6's last four columns are computational success rates for the filters, not
measured outcomes. They are recorded on separate protocols so a relevance
judgement can say so.
"""

from common import (AREAS, claim, comparison, evaluation, facets, link, missing, record,
                    result, review, rid)

SOURCE = record(
    rid("source", "bennett"), "source",
    "Atomically accurate de novo design of antibodies with RFdiffusion (Bennett et al., Nature 2025)",
    "Primary source retrieved and hashed for the 2026-10-22 de novo binder design extraction "
    "(issue #176).",
    facets=facets(),
    attributes={
        "url": "https://doi.org/10.1038/s41586-025-09721-5",
        "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12727541/fullTextXML",
        "version": "Nature, version of record; Europe PMC JATS full text for PMC12727541",
        "retrieved_at": "2026-10-22T11:55:00Z",
        "artifact_sha256": "d7876bc73c47f2cb3fcb0fa1ef917c89c9b67750a22f6402bf515f978cd1564a",
        "doi": "10.1038/s41586-025-09721-5",
        "publication_status": "peer_reviewed",
        "licence": "CC-BY-4.0",
        "media_type": "application/xml",
        "source_locator": "Results paragraph 2 and 'Improved oracles increase success rate'",
        "retrieval_method": "Europe PMC REST fullTextXML endpoint, flattened to text for reading.",
        "limitations": [
            "Developer-reported: the authors fine-tuned RFdiffusion, chose the targets and ran the "
            "screens.",
            "The main text states '95 designs per target' for the SPR-screened campaigns, while "
            "Supplementary Methods Table 6 prints 96 designs screened for each of them.",
        ],
        "evidence_concerns": [
            {
                "source_id": rid("source", "bennett"),
                "message": (
                    "The main text says 'at lower throughput with Escherichia coli expression and "
                    "single-concentration surface plasmon resonance (SPR; 95 designs per target; TcdB, "
                    "IL-7Ra and influenza haemagglutinin)', but Supplementary Methods Table 6 prints 96 "
                    "designs screened for TcdB, IL7R and H1 stem. Table 6's value is recorded because "
                    "it is the chosen table; the main text figure is 95."
                ),
                "source_locator": "Results paragraph 2; Supplementary Methods Table 6, column 'Designs "
                                  "screened'",
                "artifact_sha256": "d7876bc73c47f2cb3fcb0fa1ef917c89c9b67750a22f6402bf515f978cd1564a",
                "review_date": "2026-10-22",
            },
        ],
    },
)

SOURCE_SI = record(
    rid("source", "bennett-si"), "source",
    "Bennett 2025 Supplementary Information, including Supplementary Methods Tables 5 and 6",
    "Supplementary Information PDF retrieved and hashed for the 2026-10-22 de novo binder design "
    "extraction (issue #176).",
    facets=facets(),
    attributes={
        "url": "https://doi.org/10.1038/s41586-025-09721-5",
        "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12727541/supplementaryFiles",
        "version": "Supplementary Information PDF 41586_2025_9721_MOESM1_ESM.pdf, 129 pages, "
                   "InDesign 17.4, ModDate 2026-09-15",
        "retrieved_at": "2026-10-22T12:05:00Z",
        "artifact_sha256": "f5d4fc4f3a65a2dc3ab696e165bb86bf150b2437cdc1a7046cfbecae8ccab05c",
        "doi": "10.1038/s41586-025-09721-5",
        "publication_status": "peer_reviewed",
        "licence": "CC-BY-4.0",
        "media_type": "application/pdf",
        "artifact_member": "41586_2025_9721_MOESM1_ESM.pdf, extracted from the Europe PMC "
                           "supplementaryFiles archive for PMC12727541",
        "source_locator": "Section 6.8 'VHH Design Campaigns'; Supplementary Methods Tables 5 and 6 "
                          "(page 67)",
        "retrieval_method": (
            "Europe PMC REST supplementaryFiles endpoint. The returned archive has no end-of-central-"
            "directory record, so unzip and Python zipfile both refuse it; bsdtar read it as a stream "
            "and extracted this member, which pdfinfo confirms is a complete 129-page PDF. The hash is "
            "of the extracted member, not of the truncated archive."
        ),
        "hash_scope": "SHA-256 of the Supplementary Information PDF as extracted from one retrieval of "
                      "the supplementary archive on 2026-10-22. The archive itself was truncated "
                      "(103,690,987 bytes, SHA-256 "
                      "6b1bd61ba4d69d5393f56e0e0d12bb4349b45ce12496a1d3e6a5a8467c39203a) and is not "
                      "the pinned artifact.",
        "limitations": [
            "Section 6.8 says 'We designed VHHs against 6 targets in total' and points at Table 5, "
            "which lists seven rows including HIV Env. Table 6 covers the five targets for which "
            "binders were identified.",
            "Table 6's last four columns are computational success rates under design-time filters, not "
            "measured outcomes.",
            "The caption states that for the fine-tuned RF2 columns 'hotspot proportion = 1 was used' "
            "for filtering in this work, and that this 'is likely not the most predictive setting'.",
        ],
    },
)

PIPELINE = record(
    rid("pipeline", "bennett-rfdiffusion-antibody"), "pipeline",
    "Fine-tuned RFdiffusion antibody design pipeline (RFantibody)",
    "A version of RFdiffusion fine-tuned predominantly on antibody complex structures designs antibody "
    "variable-domain backbones against a specified epitope, ProteinMPNN designs their sequences, and a "
    "fine-tuned RoseTTAFold2 filters the designs.",
    facets=facets(method_types=["specialist"]),
    source_ids=[SOURCE["id"]],
    links=[link("variant_of", "discovery-model-rfdiffusion")],
    attributes={
        "reported_name": "fine-tuned RFdiffusion",
        "version": "As published in Nature 2025 (doi 10.1038/s41586-025-09721-5); released as "
                   "RosettaCommons/RFantibody",
        "access": "Released as a single repository, free for academic, personal and commercial use "
                  "(https://github.com/RosettaCommons/RFantibody).",
        "provenance_note": "Created from the Bennett 2025 paper for the 2026-10-22 binder design pass.",
        "source_locator": "Results paragraph 1; Fig. 1; Code availability",
    },
)

CONFIG = record(
    rid("config", "bennett", "rfdiffusion-vhh"), "configuration",
    "Fine-tuned RFdiffusion VHH design with fine-tuned RoseTTAFold2 filtering at hotspot proportion 1",
    "The VHH design campaign configuration: 200 fine-tuned RFdiffusion backbones per target, the best "
    "of eight ProteinMPNN sequences per backbone, filtered by fine-tuned RoseTTAFold2 with all "
    "interface hotspots provided.",
    facets=facets(method_types=["specialist"]),
    source_ids=[SOURCE["id"], SOURCE_SI["id"]],
    links=[link("configuration_of", PIPELINE["id"]),
           link("uses_model", "discovery-model-proteinmpnn")],
    attributes={
        "reported_name": "fine-tuned RFdiffusion",
        "version": "Nature 2025 version of record",
        "parameters": (
            "200 backbones designed per target; the best of eight ProteinMPNN sequences per backbone by "
            "the filtering method; fine-tuned RoseTTAFold2 as the filter with hotspot proportion = 1, "
            "which the Table 6 caption notes 'is likely not the most predictive setting'. Filter "
            "success was defined as Ca RMSD < 2 A and pAE interaction < 10."
        ),
        "selection": "Designs passing the fine-tuned RoseTTAFold2 filter at hotspot proportion 1.",
        "limitations": [
            "The filter is the authors' own fine-tuned RoseTTAFold2, so design and selection are not "
            "independent. The paper states the filter's power is limited and that this 'probably "
            "accounts for the low experimental success rates'.",
        ],
        "access_reuse": "Released as RosettaCommons/RFantibody.",
        "method_role": "design",
        "foundation_model_eligible": False,
        "source_locator": "Supplementary Methods Table 6 caption; Section 6.8",
    },
)

# Supplementary Methods Table 5, every row as printed.
TABLE_5 = {
    "hivenv": ("HIV Env", "2NY7", "A371, A375, A435, A475"),
    "rbd": ("SARS-CoV-2 RBD", "6M0J", "B492, B493, B494, B495, B496, B497"),
    "rsv1": ("RSV-F Site I", "7LVW", "D469, D384"),
    "rsv3": ("RSV-F Site III", "7LUC", "T305, T456"),
    "h1stem": ("Influenza Hemagglutinin", "5VLI", "B521, B545, B552"),
    "tcdb": ("TcdB", "6C0B", "A1433, A1435, A1437, A1438, A1493"),
    "il7r": ("IL-7 Receptor α", "3DI3", "B81, B139, B192"),
}

TARGET_DETAIL = {
    "hivenv": "HIV envelope glycoprotein",
    "rbd": "SARS-CoV-2 spike receptor-binding domain",
    "rsv1": "Respiratory syncytial virus F protein, site I",
    "rsv3": "Respiratory syncytial virus F protein, site III",
    "h1stem": "Influenza H1 haemagglutinin stem",
    "tcdb": "Clostridioides difficile toxin B",
    "il7r": "Interleukin-7 receptor alpha",
}

# Supplementary Methods Table 6, every cell. Each entry is one printed row.
# (row key, Table 6 target label, dataset key, designs screened, initial screening method,
#  SPR confirmed binders, success rate by SPR, CDR-H3 similarity, OrthoRep fold improvement,
#  RF2 hotspot 1, RF2 hotspot 0.1, RF2 hotspot 0.0, AF3)
TABLE_6 = [
    ("tcdb-spr", "TcdB", "tcdb", 96, "SPR", "2", "2%", "22.2%", "~100x",
     "41.0", "33.5", "27.5", "27.5"),
    ("il7r-spr", "IL7R", "il7r", 96, "SPR", "0", "0%", "N/A", "N/A",
     "34.5", "27.0", "12.5", "5.0"),
    ("h1stem-spr", "H1 stem", "h1stem", 96, "SPR", "1", "1%", "33.4%", "N/A",
     "11.5", "7.5", "3.5", "5.0"),
    ("h1stem-ysd", "H1 stem", "h1stem", 9000, "YSD", "20", "0.2%", "(33.4%)", "~1000x",
     "(11.5)", "(7.5)", "(3.5)", "5.0"),
    ("rbd-ysd", "SARS-CoV-2 RBD", "rbd", 9000, "YSD", "5", "0.06%", "20.4%", "~1000x",
     "28.0", "23.5", "11.0", "0.0"),
    ("rsv3-ysd", "RSV site 3", "rsv3", 9000, "YSD", "1", "0.01%", "N/A", "N/A",
     "25.0", "3.0", "1.0", "0.0*"),
]

VHH_LIMITS = [
    "Developer-reported: the authors fine-tuned RFdiffusion, chose the targets, chose the filter and "
    "ran the screens.",
    "The designs tested are those that passed the authors' own fine-tuned RoseTTAFold2 filter at "
    "hotspot proportion 1, which the Table 6 caption calls 'likely not the most predictive setting', so "
    "design and selection are coupled.",
    "No conventional comparator (immunisation, hybridoma, phage or yeast library selection from a "
    "random library) was run on these targets.",
    "No uncertainty is printed for any rate.",
    "RSV-F site I and HIV Env appear in Supplementary Methods Table 5 but have no row in Table 6; the "
    "caption restricts Table 6 to 'the 5 targets for which de novo VHH binders were identified', so "
    "their outcomes are not printed.",
]

PROTOCOLS = {
    "spr96": record(
        rid("protocol", "bennett", "vhh-ecoli-spr-96"), "protocol",
        "Bennett VHH design, E. coli expression and single-concentration SPR screen of 96 designs",
        "Share of designed VHHs confirmed as binders by single-concentration SPR after E. coli "
        "expression, out of 96 designs screened per target.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_SI["id"]],
        attributes={
            "protocol": (
                "Computationally filtered VHH designs are expressed in Escherichia coli and screened at "
                "a single concentration by surface plasmon resonance. Table 6 reports the number of "
                "SPR-confirmed binders and the success rate out of 96 designs screened."
            ),
            "version": "Nature 2025 version of record; Supplementary Methods Table 6",
            "metric": "hit-rate",
            "metric_direction": "higher",
            "metric_qualifier": "SPR-confirmed binders out of designs screened, E. coli expression, "
                                "single-concentration SPR",
            "unit": "percent",
            "denominator": 96,
            "success_threshold": {
                "criterion": "confirmed as a binder by single-concentration SPR",
                "note": "No numeric SPR response or affinity threshold is printed.",
                "locator": "Supplementary Methods Table 6, column 'SPR confirmed binders'",
            },
            "selection": "Designs passing the fine-tuned RoseTTAFold2 filter at hotspot proportion 1, "
                         "from 200 backbones per target with the best of 8 ProteinMPNN sequences each.",
            "selection_bias": "The filter is the authors' own.",
            "source_locator": "Supplementary Methods Table 6, rows with 'Initial screening method' "
                              "= SPR",
            "limitations": VHH_LIMITS,
        },
    ),
    "ysd9000": record(
        rid("protocol", "bennett", "vhh-yeast-display-9000"), "protocol",
        "Bennett VHH design, yeast surface display screen of 9,000 designs with SPR confirmation",
        "Share of designed VHHs confirmed as binders after high-throughput yeast surface display "
        "screening and SPR confirmation, out of 9,000 designs screened per target.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_SI["id"]],
        attributes={
            "protocol": (
                "Computationally filtered VHH designs are screened at high throughput by yeast surface "
                "display, and hits are confirmed by surface plasmon resonance. Table 6 reports the "
                "number of SPR-confirmed binders and the success rate out of 9,000 designs screened."
            ),
            "version": "Nature 2025 version of record; Supplementary Methods Table 6",
            "metric": "hit-rate",
            "metric_direction": "higher",
            "metric_qualifier": "SPR-confirmed binders out of designs screened, yeast surface display "
                                "with SPR confirmation",
            "unit": "percent",
            "denominator": 9000,
            "success_threshold": {
                "criterion": "yeast-display hit confirmed as a binder by SPR",
                "note": "No numeric display signal or affinity threshold is printed.",
                "locator": "Supplementary Methods Table 6, column 'SPR confirmed binders'",
            },
            "selection": "Designs passing the fine-tuned RoseTTAFold2 filter at hotspot proportion 1.",
            "selection_bias": "The filter is the authors' own.",
            "comparison_limit": "A 9,000-design display screen and a 96-design SPR screen are different "
                                "experiments on the same designs; the paper screened H1 stem both ways "
                                "and reports 1% and 0.2%.",
            "source_locator": "Supplementary Methods Table 6, rows with 'Initial screening method' "
                              "= YSD",
            "limitations": VHH_LIMITS,
        },
    ),
    "rf2": record(
        rid("protocol", "bennett", "insilico-rf2-success"), "protocol",
        "Bennett VHH computational success rate under the fine-tuned RoseTTAFold2 filter",
        "Share of designed VHHs that pass the fine-tuned RoseTTAFold2 filter, at three proportions of "
        "interface hotspots provided to the filter.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_SI["id"]],
        attributes={
            "protocol": (
                "200 backbones are designed per target and the best of eight ProteinMPNN sequences per "
                "backbone is predicted with fine-tuned RoseTTAFold2. Success is defined as Ca RMSD "
                "below 2 A and pAE interaction below 10. Three levels of provided privileged "
                "information, hotspot proportion 1, 0.1 and 0.0, are reported separately."
            ),
            "version": "Nature 2025 version of record; Supplementary Methods Table 6",
            "metric": "success-rate",
            "metric_direction": "higher",
            "metric_qualifier": "computational filter pass rate, fine-tuned RoseTTAFold2, Ca RMSD below "
                                "2 A and pAE interaction below 10",
            "unit": "percent",
            "success_threshold": {
                "criterion": "Ca RMSD < 2 A and pAE Interaction < 10",
                "locator": "Supplementary Methods Table 6 caption",
            },
            "scope_limitations": (
                "An in silico filter pass rate, not a measured outcome. The Table 6 caption gives its "
                "purpose as providing 'an estimate of the compute requirements required to generate "
                "libraries'."
            ),
            "source_locator": "Supplementary Methods Table 6, columns 'Success rate (%) (RF2, hotspot "
                              "proportion = 1 / 0.1 / 0.0)'",
            "limitations": [
                "An in silico filter pass rate, not a measured outcome.",
                "The filter is the authors' own fine-tuned RoseTTAFold2, and the caption states that "
                "hotspot proportion 1, the setting used for filtering in the work, 'is likely not the "
                "most predictive setting'.",
                "The H1 stem 9,000-design row repeats the 96-design row's values in parentheses, "
                "because both come from the same design campaign.",
            ],
        },
    ),
    "af3": record(
        rid("protocol", "bennett", "insilico-af3-success"), "protocol",
        "Bennett VHH computational success rate under an AlphaFold3 filter",
        "Share of designed VHHs that pass an AlphaFold3 filter, defined as Ca RMSD below 5 A over the "
        "whole complex and ipTM above 0.5.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_SI["id"]],
        attributes={
            "protocol": (
                "The same design sets are predicted with AlphaFold3 and scored as successful where Ca "
                "RMSD over the whole complex is below 5 A and ipTM is above 0.5. Unlike the fine-tuned "
                "RoseTTAFold2 filter, AlphaFold3 does not fix the target, so a cropped target that "
                "AlphaFold3 re-predicts inaccurately drives the rate down."
            ),
            "version": "Nature 2025 version of record; Supplementary Methods Table 6",
            "metric": "success-rate",
            "metric_direction": "higher",
            "metric_qualifier": "computational filter pass rate, AlphaFold3, Ca RMSD below 5 A over the "
                                "whole complex and ipTM above 0.5",
            "unit": "percent",
            "success_threshold": {
                "criterion": "Ca RMSD < 5 A over the whole complex and ipTM > 0.5",
                "locator": "Supplementary Methods Table 6 caption",
            },
            "scope_limitations": (
                "An in silico filter pass rate, not a measured outcome, and retrospective: AlphaFold3 "
                "was released after the design work."
            ),
            "source_locator": "Supplementary Methods Table 6, column 'Success rate (%) (AF3)'",
            "limitations": [
                "An in silico filter pass rate, not a measured outcome.",
                "Retrospective: AlphaFold3 was released after the design work in the study.",
                "The caption states that 'in some cases, the cropped target used during design was not "
                "accurate re-predicted by AF3 ... and hence the success rates are very low', and that "
                "'success rates would likely be higher with contiguous (non-cropped) targets'.",
                "The RSV site 3 value carries an asterisk: 'RSV site 3 target epitope was not correctly "
                "predicted with AF3 (RMSD = 19A) in its cropped form used in the design methods'.",
            ],
        },
    ),
}

XML_METHOD = ["transcription"]
SI_METHOD = ["pdf-text-parse", "transcription"]
SI_HOW = ("Transcribed by hand from the pdftotext -layout text layer of the pinned Supplementary "
          "Information PDF, page 67. The table is laid out across eleven columns with wrapped headers; "
          "the column assignment was checked against the caption's description of the columns and "
          "against the main text's statement that the per-target success rates 'range from 0% to 2%'.")

DATASETS = {}
for key, (printed, pdb, hotspots) in TABLE_5.items():
    DATASETS[key] = record(
        rid("data", "bennett", key), "dataset",
        f"Bennett VHH design target {printed}",
        f"{TARGET_DETAIL[key]} as a design target for the fine-tuned RFdiffusion VHH campaigns, with "
        f"the epitope defined by the hotspot residues in Supplementary Methods Table 5.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_SI["id"]],
        attributes={
            "reported_name": printed,
            "version": "Supplementary Methods Table 5, Nature 2025 version of record",
            "accession": pdb,
            "scope_note": f"Supplementary Methods Table 5, row '{printed}': PDB accession '{pdb}'; "
                          f"hotspot residues '{hotspots}'. The target was used in cropped form during "
                          f"design.",
            "population": f"VHH designs generated against the stated epitope of {printed}",
            "source_locator": f"Supplementary Methods Table 5, row '{printed}'",
        },
    )


def build():
    out = [SOURCE, SOURCE_SI, PIPELINE, CONFIG]
    out += list(DATASETS.values())
    out += list(PROTOCOLS.values())
    rev = review(SOURCE_SI, SI_METHOD, SI_HOW)
    both = [SOURCE_SI["id"], SOURCE["id"]]

    for (row_key, label, data_key, screened, method, binders, rate, cdr, orthorep,
         rf2_1, rf2_01, rf2_00, af3) in TABLE_6:
        proto = PROTOCOLS["spr96"] if method == "SPR" else PROTOCOLS["ysd9000"]
        screen_name = ("E. coli expression and single-concentration SPR" if method == "SPR"
                       else "yeast surface display with SPR confirmation")
        ev_id = rid("eval", "bennett", row_key)
        out.append(evaluation(
            ev_id,
            f"Fine-tuned RFdiffusion VHH design against {label}, {screen_name}",
            "Developer-reported outcome transcribed from the pinned supplementary table; not "
            "reproduced.",
            source=SOURCE_SI, system=CONFIG["id"], assessment=proto["id"], data=DATASETS[data_key]["id"],
            origin="author_reported", version="Nature 2025 version of record; Supplementary Methods "
                                             "Table 6",
            comparison=comparison(
                proto["id"],
                dataset_version=f"{label}, Supplementary Methods Table 5 epitope",
                population=f"{screened} designs screened against {label}",
                inputs="Cropped target structure with the Table 5 hotspot residues as the epitope",
                adaptation="Designs filtered by the authors' fine-tuned RoseTTAFold2 at hotspot "
                           "proportion 1",
                metric_implementation=f"SPR-confirmed binders out of designs screened ({screen_name})",
                aggregation="Count per target per screening method",
                budget=f"{screened} designs screened",
            ),
            locator=f"Supplementary Methods Table 6, row '{label}' with Designs screened = {screened}",
            attrs={
                "denominator": screened,
                "endpoint": "SPR-confirmed binding",
                "candidate_selection": "Fine-tuned RoseTTAFold2 filter at hotspot proportion 1, from "
                                       "200 backbones with the best of 8 ProteinMPNN sequences each.",
                "conventional_baseline": "None run on this target.",
            },
            missing=missing(
                comparison__split=("inapplicable", "A design campaign, not a train/test split."),
            ),
        ))
        out.append(result(
            rid("result", "bennett", row_key, "hitrate"),
            f"Fine-tuned RFdiffusion VHH success rate by SPR against {label} "
            f"({screened} designs, {method})",
            "Developer-reported value transcribed from the pinned supplementary table. Not reproduced.",
            source=SOURCE_SI, evaluation_id=ev_id, printed=rate,
            numeric=rate.rstrip("%"),
            metric="hit-rate", direction="higher", unit="percent",
            qualifier=f"SPR-confirmed binders out of designs screened; initial screening method "
                      f"{method}",
            unit_detail="percent of designs screened",
            numerator=int(binders), denominator=screened,
            denominator_note=f"{screened} designs screened, from the 'Designs screened' column. The "
                             f"main text states 95 designs per target for the SPR-screened campaigns.",
            locator=f"Supplementary Methods Table 6, row '{label}' (Designs screened = {screened}), "
                    f"column 'Success rate by SPR'",
            review_block=rev, source_ids=both,
            missing=missing(uncertainty=("unreported", "No interval is printed.")),
        ))
        out.append(result(
            rid("result", "bennett", row_key, "binders"),
            f"Fine-tuned RFdiffusion SPR-confirmed VHH binders against {label} "
            f"({screened} designs, {method})",
            "Developer-reported count transcribed from the pinned supplementary table. Not reproduced.",
            source=SOURCE_SI, evaluation_id=ev_id, printed=binders, numeric=binders,
            metric="count", direction="higher", unit="count",
            qualifier=f"SPR-confirmed binders; initial screening method {method}",
            unit_detail="designs",
            numerator=int(binders), denominator=screened,
            denominator_note=f"{screened} designs screened.",
            locator=f"Supplementary Methods Table 6, row '{label}' (Designs screened = {screened}), "
                    f"column 'SPR confirmed binders'",
            review_block=rev, source_ids=both,
            extra={"printed_value_basis": "A stated count of confirmed binders, which is zero for "
                                          "IL7R; it is a measured zero, not a missing value."},
            missing=missing(uncertainty=("inapplicable", "An exact count.")),
        ))

        # The four computational filter columns.
        for proto_key, col_label, qualifier, printed in [
            ("rf2", "Success rate (%) (RF2, hotspot proportion = 1)",
             "fine-tuned RoseTTAFold2 filter, hotspot proportion 1", rf2_1),
            ("rf2", "Success rate (%) (RF2, hotspot proportion = 0.1)",
             "fine-tuned RoseTTAFold2 filter, hotspot proportion 0.1", rf2_01),
            ("rf2", "Success rate (%) (RF2, hotspot proportion = 0.0)",
             "fine-tuned RoseTTAFold2 filter, hotspot proportion 0.0", rf2_00),
            ("af3", "Success rate (%) (AF3)", "AlphaFold3 filter", af3),
        ]:
            bare = printed.strip("()*")
            tag = qualifier.replace(" ", "-").replace(",", "").replace(".", "-").lower()
            ins_ev = rid("eval", "bennett", row_key, "insilico", proto_key,
                         tag.split("hotspot-proportion-")[-1] if "hotspot" in tag else "af3")
            out.append(evaluation(
                ins_ev,
                f"Fine-tuned RFdiffusion VHH computational success rate against {label}, {qualifier}",
                "Developer-reported in silico filter pass rate transcribed from the pinned "
                "supplementary table; not a measured outcome and not reproduced.",
                source=SOURCE_SI, system=CONFIG["id"], assessment=PROTOCOLS[proto_key]["id"],
                data=DATASETS[data_key]["id"],
                origin="author_reported",
                version="Nature 2025 version of record; Supplementary Methods Table 6",
                comparison=comparison(
                    PROTOCOLS[proto_key]["id"],
                    dataset_version=f"{label}, Supplementary Methods Table 5 epitope",
                    population="200 backbones per target, best of 8 ProteinMPNN sequences each",
                    inputs="Cropped target structure with the Table 5 hotspot residues as the epitope",
                    adaptation=qualifier,
                    metric_implementation="Share of designs passing the stated structural and "
                                          "confidence thresholds",
                    aggregation="Per target",
                    budget="200 backbones designed per target",
                ),
                locator=f"Supplementary Methods Table 6, row '{label}' (Designs screened = {screened}), "
                        f"column '{col_label}'",
                attrs={"retrospective": proto_key == "af3"},
                missing=missing(
                    comparison__split=("inapplicable", "A design campaign, not a train/test split."),
                ),
            ))
            out.append(result(
                rid("result", "bennett", row_key, "insilico", proto_key,
                    tag.split("hotspot-proportion-")[-1] if "hotspot" in tag else "af3"),
                f"Fine-tuned RFdiffusion VHH computational success rate against {label}, {qualifier} "
                f"({screened}-design row)",
                "Developer-reported in silico filter pass rate transcribed from the pinned "
                "supplementary table. A pipeline filter, not a measured outcome.",
                source=SOURCE_SI, evaluation_id=ins_ev, printed=printed, numeric=bare,
                metric="success-rate", direction="higher", unit="percent",
                qualifier=qualifier + ("; value printed in parentheses because it repeats the "
                                       "96-design row from the same design campaign"
                                       if printed.startswith("(") else ""),
                unit_detail="percent of designs predicted",
                locator=f"Supplementary Methods Table 6, row '{label}' (Designs screened = "
                        f"{screened}), column '{col_label}'",
                review_block=rev, source_ids=both,
                extra=({"source_anomaly": "The printed cell carries an asterisk: 'RSV site 3 target "
                                          "epitope was not correctly predicted with AF3 (RMSD = 19A) "
                                          "in its cropped form used in the design methods'."}
                       if printed.endswith("*") else None),
                missing=missing(uncertainty=("unreported", "No interval is printed.")),
            ))

        # The two remaining columns are descriptive, recorded as claims.
        out.append(claim(
            rid("claim", "bennett", row_key, "cdrh3-similarity"),
            f"CDR-H3 mean sequence similarity of {label} binders ({screened}-design row)",
            f"Supplementary Methods Table 6 prints the CDR-H3 mean sequence similarity of the confirmed "
            f"{label} binders as {cdr}.",
            source=SOURCE_SI, subject=DATASETS[data_key]["id"],
            field="cdr_h3_mean_sequence_similarity_of_binders",
            value=cdr,
            locator=f"Supplementary Methods Table 6, row '{label}' (Designs screened = {screened}), "
                    f"column 'CDR-H3 mean sequence similarity of binders (%)'",
            review_block=rev, source_ids=both,
        ))
        out.append(claim(
            rid("claim", "bennett", row_key, "orthorep"),
            f"OrthoRep affinity-maturation fold improvement for {label} ({screened}-design row)",
            f"Supplementary Methods Table 6 prints the approximate improvement in affinity brought by "
            f"OrthoRep affinity maturation for {label} as {orthorep}.",
            source=SOURCE_SI, subject=DATASETS[data_key]["id"],
            field="orthorep_fold_improvement_in_affinity",
            value=orthorep,
            locator=f"Supplementary Methods Table 6, row '{label}' (Designs screened = {screened}), "
                    f"column 'OrthoRep fold improvement in affinity'",
            review_block=rev, source_ids=both,
        ))

    out.append(claim(
        rid("claim", "bennett", "iptm-filter-retrospective"),
        "Only 9% of the ordered Bennett VHH designs have AlphaFold3 ipTM above 0.6",
        "The paper's retrospective analysis finds that AlphaFold3 interface pTM separates binders from "
        "non-binders with an area under the curve of 0.86, and that only 9% of the ordered VHH designs "
        "have ipTM above 0.6, so the tested set was chosen by a filter the authors now consider weak.",
        source=SOURCE, subject=CONFIG["id"], field="filter_power",
        value=(
            "Results 'Improved oracles increase success rate', verbatim: 'We found that the AlphaFold3 "
            "interface predicted template modelling (ipTM) score, a measure of model confidence over "
            "the interface, is predictive of binding success (area under the curve = 0.86; Extended "
            "Data Fig. 10a,b). Overall, only 9% of our ordered VHH designs have an ipTM > 0.6, "
            "suggesting that success rate will be improved by incorporation of an ipTM filter.' And for "
            "the scFv libraries: 'Only 4% of the initial design library has ipTM > 0.85, whereas 5 out "
            "of the 6 experimentally confirmed designs pass this threshold.' The paper also states that "
            "the fine-tuned RoseTTAFold2 filter's 'filtering power ... is limited (at least with the "
            "settings used; providing 100% of interface hotspots)' and that this 'probably accounts for "
            "the low experimental success rates'."
        ),
        locator="Results 'Improved oracles increase success rate'",
        review_block=review(SOURCE, XML_METHOD,
                            "Transcribed by hand from the Europe PMC JATS full text of the pinned "
                            "article, flattened to plain text."),
    ))

    out.append(claim(
        rid("claim", "bennett", "targets-without-table6-row"),
        "Two Bennett VHH design targets have no outcome row",
        "Supplementary Methods Table 5 lists seven design targets and Table 6 reports five, because its "
        "caption restricts it to the targets for which binders were identified. RSV-F site I and HIV "
        "Env therefore have no printed outcome, and their absence is not a recorded zero.",
        source=SOURCE_SI, subject=PIPELINE["id"], field="targets_without_printed_outcome",
        value=(
            "Supplementary Methods Table 5 rows: HIV Env (2NY7), SARS-CoV-2 RBD (6M0J), RSV-F Site I "
            "(7LVW), RSV-F Site III (7LUC), Influenza Hemagglutinin (5VLI), TcdB (6C0B), IL-7 Receptor "
            "alpha (3DI3). Section 6.8 states 'We designed VHHs against 6 targets in total', which does "
            "not match the seven rows. Table 6's caption states 'For 5 targets for which de novo VHH "
            "binders were identified, details are provided', and Table 6 has rows only for TcdB, IL7R, "
            "H1 stem (twice), SARS-CoV-2 RBD and RSV site 3. No outcome is printed for RSV-F site I or "
            "HIV Env, and none is inferred here."
        ),
        locator="Supplementary Methods Tables 5 and 6; Section 6.8",
        review_block=rev, source_ids=both,
    ))

    return out
