"""AlphaProteo (arXiv:2409.08022v1) Table 1, Table S2 and Table S3.

Section S4.1 is the reason the AlphaProteo and RFdiffusion arms are kept as two
separate evaluations rather than one comparison: the authors did not run
RFdiffusion. They downloaded the published RFdiffusion design sequences and
synthesised and tested those by yeast display alongside their own designs. The
assay is shared; the selection funnel is not, so every comparison field that
describes selection, population or budget is null.
"""

from common import (AREAS, claim, comparison, evaluation, facets, link, missing, record,
                    result, review, rid)

SOURCE = record(
    rid("source", "alphaproteo"), "source",
    "De novo design of high-affinity protein binders with AlphaProteo (Zambaldi et al., arXiv 2024)",
    "Primary source retrieved and hashed for the 2026-10-22 de novo binder design extraction (issue #176).",
    facets=facets(),
    attributes={
        "url": "https://arxiv.org/abs/2409.08022v1",
        "artifact_url": "https://arxiv.org/pdf/2409.08022v1",
        "version": "arXiv version 1, posted 2024-09-12; full-text PDF (49 pages)",
        "retrieved_at": "2026-10-22T11:53:00Z",
        "artifact_sha256": "953b35644c0fa06ff090d7614c2e19525831f8fde50242e176d54474133c5a42",
        "publication_status": "preprint",
        "licence": "CC-BY-NC-SA-4.0",
        "media_type": "application/pdf",
        "source_locator": "Table 1, Table S2, Table S3, Sections S1.2.1, S2, S4.1 and S4.2",
        "retrieval_method": (
            "curl to the arXiv PDF endpoint. The search pass could not fetch this artifact because it "
            "exceeds the 10 MB fetch limit (12,333,400 bytes), so it was downloaded with curl and read "
            "with pdftotext -layout rather than through a page fetch."
        ),
        "hash_scope": "SHA-256 of one retrieval of the arXiv v1 PDF on 2026-10-22.",
        "limitations": [
            "Preprint, not peer reviewed.",
            "Developer-reported. The AlphaProteo authors built AlphaProteo, chose the targets, ran the "
            "assay and selected which designs to test.",
            "The hit definition is an instrument cutoff on a flow-cytometry binding signal, not an "
            "affinity, so these rates are not comparable with the BLI or SPR hit rates in other sources.",
            "Table 1's AlphaProteo column pools three different design systems (v1, v1 with improved "
            "filters, and v2) for SC2RBD, PD-L1, TrkA and TNF-alpha. Table S2 separates them and is the "
            "more informative table.",
            "The 'Other design methods' and 'RFdiffusion (published)' rows copy values from other "
            "publications, with some values replaced by the AlphaProteo authors' own HTRF measurements "
            "(Section S4.2). They are recorded as claims, not as results.",
            "The licence was read from the arXiv abstract page, not from the PDF bytes.",
        ],
        "evidence_concerns": [
            {
                "source_id": rid("source", "alphaproteo"),
                "message": (
                    "Table S2 prints the RFdiffusion yeast-display success rate for IL-7RA as 16.8% and "
                    "Table 1 rounds it to 17, but Section S4.1 states it in the text as '16% versus 33%'. "
                    "Section S4.1 also states TrkA as '0% (versus 6%)' where Table S2 prints 0.0 and 6.3. "
                    "The table values are recorded; the text rounds down rather than to nearest."
                ),
                "source_locator": "Table 1; Table S2; Section S4.1",
                "artifact_sha256": "953b35644c0fa06ff090d7614c2e19525831f8fde50242e176d54474133c5a42",
                "review_date": "2026-10-22",
            },
        ],
    },
)

PIPELINE = record(
    rid("pipeline", "alphaproteo"), "pipeline", "AlphaProteo",
    "AlphaProteo generates binder structures and sequences conditioned on a target structure and "
    "selects which candidates to test with a learned filter.",
    facets=facets(method_types=["specialist"]),
    source_ids=[SOURCE["id"]],
    attributes={
        "reported_name": "AlphaProteo",
        "version": "v1 and v2 generative models, as reported in arXiv:2409.08022v1",
        "access": "Not released. The paper describes a closed system.",
        "provenance_note": "Created from the AlphaProteo preprint for the 2026-10-22 binder design pass.",
        "source_locator": "Section 2, Figure 1A",
    },
)

# One configuration per design system the source distinguishes. Table 1 pools the
# first three for four of its targets; Table S2 keeps them apart.
CONFIGS = {}
for key, name, params, locator in [
    ("v1", "AlphaProteo v1",
     "v1 generative model with the original automated filter; between 47 and 172 candidates chosen per "
     "target from a larger in silico set",
     "Table S2, row 'AlphaProteo v1'; Section 2.1.1"),
    ("v1-improved-filter", "AlphaProteo v1 with improved filters",
     "v1 generative model with an improved filter, run against SC2RBD and PD-L1 only",
     "Table S2, row 'AlphaProteo v1 (improved filters)'; Section S2"),
    ("v2", "AlphaProteo v2",
     "v2 generative model, run against PD-L1, TrkA and TNF-alpha",
     "Table S2, rows 'AlphaProteo v2'; Section S2"),
    ("pooled", "AlphaProteo, pooled over tested design systems",
     "All designs tested for a target, pooled over the v1, v1-improved-filter and v2 systems as Table 1 "
     "reports them",
     "Table 1, rows 'AlphaProteo'; Section S2 'For simplicity, the results in Table 1 are pooled over all "
     "tested designs for each target.'"),
]:
    CONFIGS[key] = record(
        rid("config", "alphaproteo", key), "configuration", name,
        f"AlphaProteo binder design as configured for {name.lower()}: {params}.",
        facets=facets(method_types=["specialist"]),
        source_ids=[SOURCE["id"]],
        links=[link("configuration_of", PIPELINE["id"])],
        attributes={
            "reported_name": name,
            "version": "arXiv:2409.08022v1",
            "parameters": params,
            "access_reuse": "Closed system; run by the authors. Not available to reuse.",
            "method_role": "design",
            "source_locator": locator,
            "foundation_model_eligible": False,
        },
    )

# The RFdiffusion arm. Section S4.1: the authors downloaded the published designs
# and tested them in their own assay. This is not RFdiffusion as run by them.
CONFIGS["rfdiffusion-published-designs"] = record(
    rid("config", "rfdiffusion-published-designs-alphaproteo-yeast"), "configuration",
    "Published RFdiffusion designs, re-synthesised and tested by the AlphaProteo authors",
    "The RFdiffusion binder designs published by Watson et al., re-synthesised and screened by yeast "
    "surface display and HTRF in the AlphaProteo authors' own assay.",
    facets=facets(method_types=["specialist"]),
    source_ids=[SOURCE["id"]],
    links=[link("configuration_of", "discovery-model-rfdiffusion")],
    attributes={
        "reported_name": "RFdiffusion (our measurement)",
        "version": "Design sequences as published by Watson et al. (reference [S28]), downloaded from "
                   "figshare (https://figshare.com/s/439fdd59488215753bc3)",
        "parameters": "95 published design sequences per target for IL-7RA, PD-L1 and TrkA; no design or "
                      "filtering step was run by the AlphaProteo authors",
        "access_reuse": "Design sequences published by the original authors on figshare.",
        "method_role": "comparator",
        "model_identity_note": (
            "Section S4.1: 'we downloaded sequences of the published RFdiffusion designs and synthesized "
            "and tested them by yeast display (Section S1.2) alongside our own designs.' The designs were "
            "generated and selected by the RFdiffusion authors, so this configuration shares the assay "
            "with the AlphaProteo arms but not the design or selection step."
        ),
        "source_locator": "Table S2, row 'RFdiffusion (our measurement)'; Section S4.1",
        "foundation_model_eligible": False,
    },
)

TARGETS = {
    "bhrf1": ("BHRF1", "Epstein-Barr virus BHRF1"),
    "sc2rbd": ("SC2RBD", "SARS-CoV-2 receptor-binding domain"),
    "il7ra": ("IL-7RA", "Interleukin-7 receptor alpha"),
    "pdl1": ("PD-L1", "Programmed death-ligand 1"),
    "trka": ("TrkA", "Tropomyosin receptor kinase A"),
    "il17a": ("IL-17A", "Interleukin-17A homodimer"),
    "vegfa": ("VEGF-A", "Vascular endothelial growth factor A homodimer"),
    "tnfa": ("TNF-alpha", "Tumour necrosis factor alpha"),
}

DATASETS = {}
for key, (printed, full) in TARGETS.items():
    DATASETS[key] = record(
        rid("data", "alphaproteo", key), "dataset",
        f"AlphaProteo binder design target {printed}",
        f"{full} as the design target for the AlphaProteo binder design campaign, with the input "
        f"structure and hotspot residues given in Table S1.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "reported_name": printed,
            "version": "arXiv:2409.08022v1 Table S1",
            "assay": "Yeast surface display with flow cytometry; HTRF for KD of expressed hits",
            "population": f"Binder designs generated against {printed}, 50 to 140 amino acids long",
            "source_locator": f"Table 1, column '{printed}'; Table S1",
            "missing_metadata": missing(
                accession=("unextracted", "Table S1 gives PDB IDs and hotspot residue numbers; they were "
                                         "not transcribed in this pass."),
            ),
        },
    )

SIGNAL_LIMITS = [
    "Developer-reported: the authors built AlphaProteo, chose the targets, ran the assay and chose "
    "which designs to test.",
    "A hit is a flow-cytometry binding signal above a manually calibrated threshold, not an affinity. "
    "The thresholds 'were calibrated manually by visually inspecting scatterplots of the raw yeast "
    "data' (Section S1.2.1).",
    "The designs tested were chosen by the authors' own automated filter from a larger in silico set, "
    "so the design step and the selection step are coupled.",
    "Denominators are small (30 to 172 designs per target) and no uncertainty is printed.",
    "No conventional comparator (directed evolution, display selection or grafting) was run on these "
    "targets.",
    "Target concentrations were 0.5 to 1 micromolar, 10- to 20-fold lower than in the RFdiffusion "
    "publication, 'which may exclude lower-affinity hits' (Section S4.1).",
]

PROTOCOLS = {
    "yeast-0-2": record(
        rid("protocol", "alphaproteo", "yeast-display-signal-0-2"), "protocol",
        "AlphaProteo yeast-display binding screen, hit at binding signal above 0.2",
        "Share of tested binder designs whose yeast-display flow-cytometry binding signal exceeds 0.2.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "Designs are codon-optimised, synthesised and transformed into S. cerevisiae EBY100, "
                "displayed on the surface, incubated with biotinylated target protein, and read by flow "
                "cytometry. The binding signal is (log10 PE[FITC+,+target] - log10 PE[FITC-,+target]) - "
                "(log10 PE[FITC+,-target] - log10 PE[FITC-,-target]). Designs with a binding signal "
                "above 0.2 were considered successful binders."
            ),
            "version": "arXiv:2409.08022v1 Section S1.2.1",
            "metric": "hit-rate",
            "metric_direction": "higher",
            "metric_qualifier": "yeast-display binding signal above 0.2, over designs tested",
            "unit": "percent",
            "success_threshold": {
                "criterion": "yeast-display flow-cytometry binding signal > 0.2",
                "calibration": "thresholds calibrated manually by visual inspection of raw yeast "
                               "scatterplots",
                "locator": "Section S1.2.1",
            },
            "selection": "Between 47 and 172 candidates per target chosen by the authors' automated "
                         "filtering procedure from a larger in silico set.",
            "selection_bias": "The filter that chose the tested designs is the authors' own, so design "
                              "and selection are not independent.",
            "control": "Per-design control well with the same binder and no target, used to subtract "
                       "expression-only and target-only signal shifts.",
            "source_locator": "Section S1.2.1; Table 1; Table S2",
            "limitations": SIGNAL_LIMITS,
        },
    ),
    "yeast-1-3": record(
        rid("protocol", "alphaproteo", "yeast-display-signal-1-3"), "protocol",
        "AlphaProteo yeast-display binding screen, hit at binding signal above 1.3 (IL-17A)",
        "Share of tested binder designs whose yeast-display flow-cytometry binding signal exceeds 1.3, "
        "the threshold used for IL-17A.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "As the 0.2-threshold screen, but with the binding-signal threshold set to 1.3 'to "
                "account for background binding' on IL-17A. For VEGF-A and IL-17A an avidity method "
                "with increased sensitivity was used, in which target proteins were pre-incubated with "
                "FITC antibody and streptavidin-phycoerythrin before incubation with cells."
            ),
            "version": "arXiv:2409.08022v1 Section S1.2.1",
            "metric": "hit-rate",
            "metric_direction": "higher",
            "metric_qualifier": "yeast-display binding signal above 1.3, over designs tested",
            "unit": "percent",
            "success_threshold": {
                "criterion": "yeast-display flow-cytometry binding signal > 1.3",
                "scope": "IL-17A only",
                "locator": "Section S1.2.1",
            },
            "comparison_limit": "A different hit threshold from the other seven targets, so IL-17A rates "
                                "are not comparable with them.",
            "source_locator": "Section S1.2.1; Table 1, column 'IL-17A'",
            "limitations": SIGNAL_LIMITS,
        },
    ),
    "htrf-kd": record(
        rid("protocol", "alphaproteo", "htrf-kd"), "protocol",
        "AlphaProteo best per-target binder affinity by HTRF",
        "Lowest dissociation constant measured among a target's expressed yeast-display hits, by "
        "homogeneous time-resolved fluorescence.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "Yeast-display hits selected for follow-up were subcloned, expressed in E. coli and "
                "titrated by HTRF. The reported value is the best (lowest) KD per target. HTRF measures "
                "both species in solution at equilibrium, unlike BLI, where one species is immobilised."
            ),
            "version": "arXiv:2409.08022v1 Sections S1.3 and S4.2; Table 1",
            "metric": "dissociation-constant",
            "metric_direction": "lower",
            "metric_qualifier": "best per-target KD by HTRF among expressed hits",
            "unit": "nanomolar",
            "aggregation": "Minimum over the expressed hits for the target.",
            "comparison_limit": (
                "A best-of value over a selected subset, so it describes the best design found, not the "
                "distribution. Section S4.2 reports that HTRF gave KD values about 10-fold higher than "
                "previously published BLI values for the BINDI and LCB1 control binders, so HTRF values "
                "are not interchangeable with BLI or SPR values."
            ),
            "source_locator": "Table 1, 'Binding KD (nM)' block; Table S2; Section S4.2",
            "limitations": [
                "Best-of-subset, not a distribution; no uncertainty is printed.",
                "Measured by HTRF, which Section S4.2 shows disagrees with published BLI values by about "
                "10-fold for two control binders.",
                "Developer-reported.",
                "The subset titrated is the yeast hits that expressed in E. coli (Table S3), so the "
                "affinity values carry the expression filter as well as the design and binding filters.",
            ],
        },
    ),
    "ecoli-funnel": record(
        rid("protocol", "alphaproteo", "ecoli-htrf-funnel"), "protocol",
        "AlphaProteo expression and HTRF confirmation funnel for yeast-display hits",
        "Counts of yeast-display hits that were selected for E. coli expression, subcloned and "
        "expressed, tested by HTRF, and showed HTRF binding.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "Yeast hits chosen for follow-up were subcloned and expressed in E. coli, then tested "
                "for binding by HTRF. Table S3 reports the count surviving each stage per target."
            ),
            "version": "arXiv:2409.08022v1 Table S3",
            "metric": "count",
            "metric_direction": "unknown",
            "metric_qualifier": "designs surviving each stage of the expression and confirmation funnel",
            "unit": "count",
            "unit_detail": "designs",
            "source_locator": "Table S3",
            "limitations": [
                "The number of yeast hits selected for E. coli expression is an author choice, not the "
                "full hit set, so these counts do not reconstruct the full funnel from the hit rates.",
                "TNF-alpha has no column in Table S3, consistent with its 0% hit rate.",
                "Developer-reported.",
            ],
        },
    ),
}

# Table 1, 'Experimental success rate (%)' block, row 'AlphaProteo'.
# printed value, designs tested, target key.
TABLE1_AP_RATE = [
    ("bhrf1", "88", "88", 94),
    ("sc2rbd", "12", "12", 172),
    ("il7ra", "25", "25", 94),
    ("pdl1", "15", "15", 159),
    ("trka", "9", "9", 131),
    ("il17a", "14", "14", 63),
    ("vegfa", "33", "33", 94),
    ("tnfa", "0", "0", 54),
]

# Table 1, 'Binding KD (nM)' block, row 'AlphaProteo'. TNF-alpha prints an en dash.
TABLE1_AP_KD = [
    ("bhrf1", "8.5", "8.5", 94),
    ("sc2rbd", "26", "26", 172),
    ("il7ra", "0.082", "0.082", 94),
    ("pdl1", "0.18", "0.18", 159),
    ("trka", "0.96", "0.96", 131),
    ("il17a", "8.4", "8.4", 63),
    ("vegfa", "0.48", "0.48", 94),
]

# Table 1, row 'RFdiffusion'.
TABLE1_RFD_RATE = [("il7ra", "17", "17", 95), ("pdl1", "13", "13", 95), ("trka", "0.0", "0.0", 95)]
TABLE1_RFD_KD = [("il7ra", "14*", "14", 95), ("pdl1", "1.6*", "1.6", 95), ("trka", "370*", "370", 95)]

# Table S2, 'Success (%)' block. (config key, target key, printed, numeric, denominator, note)
TABLE_S2_RATE = [
    ("v1", "bhrf1", "88", "88", 94, None),
    ("v1", "sc2rbd", "8.5", "8.5", 94, "hotspot conditioning"),
    ("v1", "sc2rbd", "8.5", "8.5", 47, "subset made without hotspot conditioning, marked with a dagger"),
    ("v1", "il7ra", "24.5", "24.5", 94, None),
    ("v1", "pdl1", "9.6", "9.6", 94, None),
    ("v1", "trka", "9.6", "9.6", 94, None),
    ("v1", "il17a", "14.3", "14.3", 63, None),
    ("v1", "vegfa", "33", "33", 94, None),
    ("v1", "tnfa", "0", "0", 30, None),
    ("v1-improved-filter", "sc2rbd", "29", "29", 31, None),
    ("v1-improved-filter", "pdl1", "16.1", "16.1", 31, None),
    ("v2", "pdl1", "26.5", "26.5", 34, None),
    ("v2", "trka", "8.1", "8.1", 37, None),
    ("v2", "tnfa", "0", "0", 24, None),
    ("rfdiffusion-published-designs", "il7ra", "16.8", "16.8", 95, None),
    ("rfdiffusion-published-designs", "pdl1", "12.6", "12.6", 95, None),
    ("rfdiffusion-published-designs", "trka", "0.0", "0.0", 95, None),
]

# Table S2, 'Binding KD (nM)' block.
TABLE_S2_KD = [
    ("v1", "bhrf1", "8.5", "8.5", 94, None),
    ("v1", "sc2rbd", "30", "30", 94, "hotspot conditioning"),
    ("v1", "sc2rbd", "26", "26", 47, "subset made without hotspot conditioning, marked with a dagger"),
    ("v1", "il7ra", "0.08", "0.08", 94, None),
    ("v1", "pdl1", "3.4", "3.4", 94, None),
    ("v1", "trka", "0.96", "0.96", 94, None),
    ("v1", "il17a", "8.4", "8.4", 63, None),
    ("v1", "vegfa", "0.48", "0.48", 94, None),
    ("v1-improved-filter", "sc2rbd", "33", "33", 31, None),
    ("v1-improved-filter", "pdl1", "47", "47", 31, None),
    ("v2", "pdl1", "0.18", "0.18", 34, None),
    ("v2", "trka", "60", "60", 37, None),
    ("rfdiffusion-published-designs", "il7ra", "14.1", "14.1", 95, None),
    ("rfdiffusion-published-designs", "pdl1", "1.56", "1.56", 95, None),
    ("rfdiffusion-published-designs", "trka", "370", "370", 95, None),
]

# Table S3, every cell. stage key -> (printed label, per-target counts)
TABLE_S3 = [
    ("yeast-hits-selected", "Yeast surface display hits selected for E. coli expression",
     {"bhrf1": 2, "sc2rbd": 18, "il7ra": 11, "pdl1": 21, "trka": 10, "il17a": 9, "vegfa": 31}),
    ("subcloned-expressed", "Successfully subcloned and expressed",
     {"bhrf1": 2, "sc2rbd": 17, "il7ra": 11, "pdl1": 20, "trka": 5, "il17a": 9, "vegfa": 31}),
    ("tested-htrf", "Tested by HTRF",
     {"bhrf1": 2, "sc2rbd": 17, "il7ra": 11, "pdl1": 18, "trka": 5, "il17a": 7, "vegfa": 31}),
    ("observed-htrf-binding", "Observed HTRF binding",
     {"bhrf1": 2, "sc2rbd": 14, "il7ra": 11, "pdl1": 16, "trka": 5, "il17a": 3, "vegfa": 20}),
]

PDF_METHOD = ["pdf-text-parse", "transcription"]
HOW = ("Transcribed by hand from the pdftotext -layout text layer of the pinned arXiv v1 PDF. The "
       "column assignment of Table 1 and Table S2 was checked arithmetically: the Table S2 "
       "per-system denominators sum to the Table 1 pooled denominators for every target "
       "(SC2RBD 94+47+31=172, PD-L1 94+31+34=159, TrkA 94+37=131, TNF-alpha 30+24=54) and the "
       "pooled rates and best-of KD values agree with Table 1 after rounding.")


def build():
    out = [SOURCE, PIPELINE]
    out += list(CONFIGS.values())
    out += list(DATASETS.values())
    out += list(PROTOCOLS.values())
    rev = review(SOURCE, PDF_METHOD, HOW)

    def protocol_for(target_key):
        return PROTOCOLS["yeast-1-3"] if target_key == "il17a" else PROTOCOLS["yeast-0-2"]

    # Table 1 pooled AlphaProteo rates and affinities.
    for block, rows, which in [("rate", TABLE1_AP_RATE, "rate"), ("kd", TABLE1_AP_KD, "kd")]:
        for target_key, printed, numeric, tested in rows:
            cfg = CONFIGS["pooled"]
            proto = PROTOCOLS["htrf-kd"] if which == "kd" else protocol_for(target_key)
            data = DATASETS[target_key]
            printed_target = TARGETS[target_key][0]
            ev_id = rid("eval", "alphaproteo", "table1", which, target_key)
            out.append(evaluation(
                ev_id,
                f"AlphaProteo on {printed_target}, pooled over tested design systems "
                f"({'best KD by HTRF' if which == 'kd' else 'yeast-display hit rate'}, Table 1)",
                "Developer-reported outcome transcribed from the pinned source; not reproduced.",
                source=SOURCE, system=cfg["id"], assessment=proto["id"], data=data["id"],
                origin="author_reported", version="arXiv:2409.08022v1 Table 1",
                comparison=comparison(
                    proto["id"],
                    dataset_version=f"{printed_target}, Table S1 input structure",
                    population=f"{tested} designs tested against {printed_target}",
                    inputs="Target structure and hotspot residues",
                    metric_implementation=(
                        "Best (lowest) KD among expressed hits, by HTRF" if which == "kd"
                        else "Fraction of tested designs with a yeast-display binding signal above the "
                             "stated threshold"),
                    aggregation="Pooled over all designs tested for the target",
                    budget=f"{tested} designs synthesised and assayed",
                ),
                locator=f"Table 1, column '{printed_target}', row 'AlphaProteo'",
                attrs={
                    "denominator": tested,
                    "candidate_selection": "Authors' own automated filter chose the candidates to test.",
                    "conventional_baseline": "None run on this target.",
                },
                missing=missing(
                    comparison__split=("inapplicable", "A design campaign, not a train/test split."),
                    comparison__adaptation=("inapplicable", "No adaptation step; designs are generated "
                                                            "per target."),
                ),
            ))
            if which == "rate":
                out.append(result(
                    rid("result", "alphaproteo", "table1", "hitrate", target_key),
                    f"AlphaProteo experimental success rate on {printed_target} (Table 1)",
                    "Developer-reported value transcribed from the pinned source. Not reproduced.",
                    source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
                    metric="hit-rate", direction="higher", unit="percent",
                    qualifier=(
                        "yeast-display binding signal above "
                        f"{'1.3' if target_key == 'il17a' else '0.2'}, over designs tested; pooled over "
                        "the AlphaProteo design systems tested for this target"),
                    unit_detail="percent of designs tested",
                    denominator=tested,
                    denominator_note=(
                        f"{tested} designs tested, printed in parentheses beneath the rate in Table 1. "
                        "The tested designs are those the authors' own filter selected from a larger in "
                        "silico set."),
                    locator=f"Table 1, 'Experimental success rate (%)' block, row 'AlphaProteo', "
                            f"column '{printed_target}'",
                    review_block=rev,
                    missing=missing(
                        uncertainty=("unreported", "No interval or replicate count is printed."),
                        numerator=("unreported", "Table 1 prints the rate and the denominator, not the "
                                                 "number of hits."),
                    ),
                ))
            else:
                out.append(result(
                    rid("result", "alphaproteo", "table1", "kd", target_key),
                    f"AlphaProteo best binder affinity on {printed_target} (Table 1)",
                    "Developer-reported value transcribed from the pinned source. Not reproduced.",
                    source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
                    metric="dissociation-constant", direction="lower", unit="nanomolar",
                    qualifier="best per-target KD by HTRF among expressed hits, non-optimised designs",
                    denominator=tested,
                    denominator_note=f"{tested} designs tested; the KD is the best among the subset that "
                                     f"was a yeast hit and expressed in E. coli (Table S3).",
                    locator=f"Table 1, 'Binding KD (nM)' block, row 'AlphaProteo', "
                            f"column '{printed_target}'",
                    review_block=rev,
                    missing=missing(uncertainty=("unreported", "No interval is printed.")),
                ))

    # Table 1 RFdiffusion rows: a separate evaluation on the same protocol, with every
    # comparison field describing selection, population or budget set to null.
    rfd_missing = missing(
        comparison__population=("conflicting",
            "Section S4.1 shows the RFdiffusion designs were selected by the RFdiffusion authors and the "
            "AlphaProteo designs by the AlphaProteo filter, so the two tested populations are not "
            "matched and no shared population can be stated."),
        comparison__inputs=("unreported",
            "The inputs that produced the published RFdiffusion designs are not restated here."),
        comparison__adaptation=("conflicting",
            "The filtering and selection funnels differ between the arms and parity is unverified, so "
            "this field is left null to block automatic comparison."),
        comparison__budget=("conflicting",
            "A flat 95 published designs per target against 94 to 172 AlphaProteo designs chosen per "
            "target indicates two separate ordering decisions."),
        comparison__split=("inapplicable", "A design campaign, not a train/test split."),
    )
    for which, rows in [("rate", TABLE1_RFD_RATE), ("kd", TABLE1_RFD_KD)]:
        for target_key, printed, numeric, tested in rows:
            printed_target = TARGETS[target_key][0]
            proto = PROTOCOLS["htrf-kd"] if which == "kd" else PROTOCOLS["yeast-0-2"]
            ev_id = rid("eval", "alphaproteo", "table1", "rfdiffusion", which, target_key)
            out.append(evaluation(
                ev_id,
                f"Published RFdiffusion designs on {printed_target}, measured by the AlphaProteo authors "
                f"({'best KD by HTRF' if which == 'kd' else 'yeast-display hit rate'}, Table 1)",
                "Published designs re-tested by the AlphaProteo authors in their own assay; transcribed "
                "from the pinned source and not reproduced.",
                source=SOURCE, system=CONFIGS["rfdiffusion-published-designs"]["id"],
                assessment=proto["id"], data=DATASETS[target_key]["id"],
                origin="author_reported", version="arXiv:2409.08022v1 Table 1; Section S4.1",
                comparison=comparison(
                    proto["id"],
                    dataset_version=f"{printed_target}, Table S1 input structure",
                    metric_implementation=(
                        "Best (lowest) KD, by HTRF" if which == "kd"
                        else "Fraction of tested designs with a yeast-display binding signal above 0.2"),
                    aggregation="Over the 95 published designs tested",
                ),
                locator=f"Table 1, column '{printed_target}', row 'RFdiffusion'; Section S4.1",
                attrs={
                    "denominator": tested,
                    "candidate_selection": (
                        "None by the AlphaProteo authors: the 95 designs are the ones published by the "
                        "RFdiffusion authors."),
                    "conventional_baseline": "None run on this target.",
                    "limitations": [
                        "Not RFdiffusion as run by the AlphaProteo authors. Section S4.1: they downloaded "
                        "the published design sequences and tested those.",
                        "Shares the assay with the AlphaProteo arms but not the design or selection step, "
                        "so this evaluation is deliberately not a comparison with them.",
                    ],
                },
                missing=rfd_missing,
            ))
            if which == "rate":
                out.append(result(
                    rid("result", "alphaproteo", "table1", "rfdiffusion", "hitrate", target_key),
                    f"Published RFdiffusion designs, yeast-display success rate on {printed_target} "
                    f"(Table 1)",
                    "Value measured by the AlphaProteo authors on published designs, transcribed from the "
                    "pinned source. Not reproduced.",
                    source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
                    metric="hit-rate", direction="higher", unit="percent",
                    qualifier="yeast-display binding signal above 0.2, over the 95 published "
                              "RFdiffusion designs tested",
                    unit_detail="percent of designs tested",
                    denominator=tested,
                    denominator_note="95 published RFdiffusion designs per target, printed in "
                                     "parentheses beneath the rate.",
                    locator=f"Table 1, 'Experimental success rate (%)' block, row 'RFdiffusion', "
                            f"column '{printed_target}'",
                    review_block=rev,
                    missing=missing(
                        uncertainty=("unreported", "No interval is printed."),
                        numerator=("unreported", "Table 1 prints the rate and the denominator only."),
                    ),
                ))
            else:
                out.append(result(
                    rid("result", "alphaproteo", "table1", "rfdiffusion", "kd", target_key),
                    f"Published RFdiffusion designs, best affinity on {printed_target} measured by HTRF "
                    f"(Table 1)",
                    "Value measured by the AlphaProteo authors on published designs, transcribed from the "
                    "pinned source. Not reproduced.",
                    source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
                    metric="dissociation-constant", direction="lower", unit="nanomolar",
                    qualifier="best KD among the 95 published RFdiffusion designs, measured by the "
                              "AlphaProteo authors using HTRF (asterisk in Table 1)",
                    denominator=tested,
                    locator=f"Table 1, 'Binding KD (nM)' block, row 'RFdiffusion', "
                            f"column '{printed_target}'",
                    review_block=rev,
                    extra={"printed_value_basis": "The asterisk in the printed cell marks a KD the "
                                                  "AlphaProteo authors measured themselves by HTRF."},
                    missing=missing(uncertainty=("unreported", "No interval is printed.")),
                ))

    # Table S2, the per-design-system breakdown.
    for which, rows in [("rate", TABLE_S2_RATE), ("kd", TABLE_S2_KD)]:
        for cfg_key, target_key, printed, numeric, tested, note in rows:
            printed_target = TARGETS[target_key][0]
            cfg = CONFIGS[cfg_key]
            is_rfd = cfg_key == "rfdiffusion-published-designs"
            proto = (PROTOCOLS["htrf-kd"] if which == "kd"
                     else PROTOCOLS["yeast-1-3"] if target_key == "il17a"
                     else PROTOCOLS["yeast-0-2"])
            suffix = "dagger" if note and "dagger" in note else "main"
            ev_id = rid("eval", "alphaproteo", "s2", which, cfg_key, target_key, suffix)
            out.append(evaluation(
                ev_id,
                f"{cfg['name']} on {printed_target} "
                f"({'best KD by HTRF' if which == 'kd' else 'yeast-display hit rate'}, Table S2"
                f"{', no-hotspot subset' if suffix == 'dagger' else ''})",
                "Developer-reported outcome transcribed from the pinned source; not reproduced.",
                source=SOURCE, system=cfg["id"], assessment=proto["id"], data=DATASETS[target_key]["id"],
                origin="author_reported", version="arXiv:2409.08022v1 Table S2",
                comparison=comparison(
                    proto["id"],
                    dataset_version=f"{printed_target}, Table S1 input structure",
                    population=None if is_rfd else f"{tested} designs tested against {printed_target}"
                                                   + (f" ({note})" if note else ""),
                    inputs=None if is_rfd else "Target structure and hotspot residues"
                                               + (" (no hotspot conditioning)" if suffix == "dagger"
                                                  else ""),
                    adaptation=None,
                    metric_implementation=(
                        "Best (lowest) KD among expressed hits, by HTRF" if which == "kd"
                        else "Fraction of tested designs with a yeast-display binding signal above the "
                             "stated threshold"),
                    aggregation="Over the designs tested for this design system and target",
                    budget=None if is_rfd else f"{tested} designs synthesised and assayed",
                ),
                locator=f"Table S2, column '{printed_target}', row '{cfg['attributes']['reported_name']}'"
                        + (" (dagger subset)" if suffix == "dagger" else ""),
                attrs={"denominator": tested},
                missing=(rfd_missing if is_rfd else missing(
                    comparison__split=("inapplicable", "A design campaign, not a train/test split."),
                    comparison__adaptation=("inapplicable", "No adaptation step."),
                )),
            ))
            if which == "rate":
                out.append(result(
                    rid("result", "alphaproteo", "s2", "hitrate", cfg_key, target_key, suffix),
                    f"{cfg['name']} success rate on {printed_target} (Table S2)",
                    "Developer-reported value transcribed from the pinned source. Not reproduced.",
                    source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
                    metric="hit-rate", direction="higher", unit="percent",
                    qualifier=(
                        "yeast-display binding signal above "
                        f"{'1.3' if target_key == 'il17a' else '0.2'}, over designs tested"
                        + (f"; {note}" if note else "")),
                    unit_detail="percent of designs tested",
                    denominator=tested,
                    denominator_note=f"{tested} designs tested, printed in parentheses beneath the rate.",
                    locator=f"Table S2, 'Success (%)' block, row "
                            f"'{cfg['attributes']['reported_name']}', column '{printed_target}'"
                            + (" (dagger subset)" if suffix == "dagger" else ""),
                    review_block=rev,
                    missing=missing(
                        uncertainty=("unreported", "No interval is printed."),
                        numerator=("unreported", "Table S2 prints the rate and the denominator only."),
                    ),
                ))
            else:
                out.append(result(
                    rid("result", "alphaproteo", "s2", "kd", cfg_key, target_key, suffix),
                    f"{cfg['name']} best affinity on {printed_target} (Table S2)",
                    "Developer-reported value transcribed from the pinned source. Not reproduced.",
                    source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
                    metric="dissociation-constant", direction="lower", unit="nanomolar",
                    qualifier="best KD by HTRF among the designs tested for this design system"
                              + (f"; {note}" if note else ""),
                    denominator=tested,
                    locator=f"Table S2, 'Binding KD (nM)' block, row "
                            f"'{cfg['attributes']['reported_name']}', column '{printed_target}'"
                            + (" (dagger subset)" if suffix == "dagger" else ""),
                    review_block=rev,
                    missing=missing(uncertainty=("unreported", "No interval is printed.")),
                ))

    # Table S3, the expression and confirmation funnel.
    for stage_key, stage_label, counts in TABLE_S3:
        for target_key, count in counts.items():
            printed_target = TARGETS[target_key][0]
            ev_id = rid("eval", "alphaproteo", "s3", stage_key, target_key)
            out.append(evaluation(
                ev_id,
                f"AlphaProteo {stage_label.lower()} for {printed_target} (Table S3)",
                "Developer-reported count transcribed from the pinned source; not reproduced.",
                source=SOURCE, system=CONFIGS["pooled"]["id"],
                assessment=PROTOCOLS["ecoli-funnel"]["id"], data=DATASETS[target_key]["id"],
                origin="author_reported", version="arXiv:2409.08022v1 Table S3",
                comparison=comparison(
                    PROTOCOLS["ecoli-funnel"]["id"],
                    dataset_version=f"{printed_target}, Table S1 input structure",
                    population="Yeast-display hits selected by the authors for follow-up",
                    metric_implementation="Count of designs surviving the stage",
                    aggregation="Count per target per stage",
                ),
                locator=f"Table S3, row '{stage_label}', column '{printed_target}'",
                missing=missing(
                    comparison__split=("inapplicable", "A design campaign, not a train/test split."),
                    comparison__inputs=("inapplicable", "A funnel count, not a scored prediction."),
                    comparison__adaptation=("inapplicable", "No adaptation step."),
                    comparison__budget=("unreported",
                        "Table S3 does not state how many of the target's yeast hits were available to "
                        "select from."),
                ),
            ))
            out.append(result(
                rid("result", "alphaproteo", "s3", stage_key, target_key),
                f"AlphaProteo {stage_label.lower()} for {printed_target} (Table S3)",
                "Developer-reported count transcribed from the pinned source. Not reproduced.",
                source=SOURCE, evaluation_id=ev_id, printed=str(count), numeric=str(count),
                metric="count", direction="unknown", unit="count",
                qualifier=stage_label, unit_detail="designs",
                locator=f"Table S3, row '{stage_label}', column '{printed_target}'",
                review_block=rev,
                missing=missing(
                    uncertainty=("inapplicable", "An exact count."),
                    denominator=("unreported",
                        "Table S3 does not state how many yeast hits were available to select from, so "
                        "the first stage has no printed denominator."),
                ),
            ))

    # The compilation rows, recorded as claims rather than results.
    out.append(claim(
        rid("claim", "alphaproteo", "other-design-methods-compilation"),
        "AlphaProteo Table 1 'Other design methods' rows are copied from other publications",
        "The 'Other design methods' and 'Other design methods, optimized' rows of Table 1, and the "
        "'RFdiffusion (published)' row of Table S2, copy values from other publications, and some of "
        "those values were re-measured by the AlphaProteo authors. They are recorded here as a "
        "transcription rather than as results.",
        source=SOURCE, subject=PIPELINE["id"], field="compilation_rows_not_extracted",
        value=(
            "Table 1, row 'Other design methods', Experimental success rate (%): BHRF1 18 a (17); "
            "SC2RBD 1.6 b (63); IL-7RA 0.15 c (14,912); PD-L1 13 b (16); TrkA 0.07 c (14,982); "
            "IL-17A 0.02 d (15,000); VEGF-A and TNF-alpha print an en dash. "
            "Table 1, row 'Other design methods', Binding KD (nM): BHRF1 58 a (17); SC2RBD 100 e "
            "(100,000); IL-7RA 3 c (14,912); PD-L1 0.9 b (16); TrkA 3000 c (14,982); IL-17A 47 d "
            "(15,000). Table 1, row 'Other design methods, optimized', Binding KD (nM): BHRF1 16*,a; "
            "SC2RBD 16*,e; IL-7RA 0.31 c; PD-L1 0.65 f; TrkA 1.4 c; IL-17A 0.01 d. "
            "Footnotes: a Procko et al. [35]; b Gainza et al. [11]; c Cao et al. [6]; d Berger et al. "
            "[3]; e Cao et al. [5]; f Yang et al. [45]. "
            "Table S2, row 'RFdiffusion (published)', Success (%): IL-7RA 33.7 (95); PD-L1 12.6 (95); "
            "TrkA 6.3 (95). Table S2, row 'RFdiffusion (published)', Binding KD (nM): IL-7RA 30 (95); "
            "PD-L1 1400 (95); TrkA 328 (95). "
            "Not recorded as results because the values are copied from publications this pass did not "
            "retrieve, and because Section S4.2 states that the asterisked values were measured by the "
            "AlphaProteo authors themselves by HTRF and that for PD-L1 they substituted a different "
            "design (RFD_PDL1_76, KD 1.6 nM) for the published best design (RFD_PDL1_77, KD 1.4 "
            "micromolar). That is a third party's reanalysis of another group's result."
        ),
        locator="Table 1, rows 'Other design methods' and 'Other design methods, optimized'; Table S2, "
                "row 'RFdiffusion (published)'; Sections S4.1 and S4.2",
        review_block=review(SOURCE, PDF_METHOD, HOW),
    ))

    out.append(claim(
        rid("claim", "alphaproteo", "s41-rfdiffusion-arm"),
        "Section S4.1 states that the RFdiffusion arm is the published designs re-tested, not a rerun",
        "The AlphaProteo authors did not run RFdiffusion. Section S4.1 states that they downloaded the "
        "published RFdiffusion design sequences and synthesised and tested those by yeast display "
        "alongside their own designs, because the published RFdiffusion rates rest on 96-well BLI "
        "measurements that were impractical for them to perform.",
        source=SOURCE, subject=CONFIGS["rfdiffusion-published-designs"]["id"],
        field="evaluation_actor",
        value=(
            "Section S4.1, verbatim: 'Published experimental success rates of RFdiffusion were based on "
            "96-well biolayer interferometry (BLI) measurements [S28], which are impractical for us to "
            "perform on our own designs. Therefore, to quantitatively compare success rates, we "
            "downloaded sequences of the published RFdiffusion designs and synthesized and tested them "
            "by yeast display (Section S1.2) alongside our own designs. Our results matched the "
            "published success rates for PD-L1 but were 2-fold lower for IL-7RA (16% versus 33%) and 0% "
            "for TrkA (versus 6%) (Table S2). This is potentially due to differences between the yeast "
            "surface environment versus purified proteins, as well as our use of 10- to 20-fold lower "
            "target concentrations (0.5-1 uM versus 10 uM in [S28]), which may exclude lower-affinity "
            "hits.' Section S4.1 therefore states a shared assay and does not state a shared selection "
            "funnel: the AlphaProteo candidates were chosen by the authors' own filter from a larger in "
            "silico set, while the RFdiffusion candidates are the 95 designs the RFdiffusion authors "
            "published."
        ),
        locator="Section S4.1",
        review_block=review(SOURCE, PDF_METHOD, HOW),
    ))

    out.append(claim(
        rid("claim", "alphaproteo", "table1-pools-design-systems"),
        "AlphaProteo Table 1 pools three different design systems",
        "Table 1's AlphaProteo column is not one design system. Section S2 states that the results are "
        "pooled over all tested designs per target, and Table S2 shows that for SC2RBD, PD-L1, TrkA and "
        "TNF-alpha the pooled set mixes the v1 model, v1 with improved filters, and v2.",
        source=SOURCE, subject=CONFIGS["pooled"]["id"], field="aggregation_scope",
        value=(
            "Section S2, verbatim: 'We experimentally tested a design system containing the v1 model "
            "against all 7 targets, a v1-based system with an improved filter against SC2RBD and PD-L1, "
            "and a v2-based system on PD-L1 and TrkA (Table S2). Both improving the filter and the model "
            "resulted in increased experimental success rates. For simplicity, the results in Table 1 "
            "are pooled over all tested designs for each target.' The Table S2 denominators sum to the "
            "Table 1 denominators: SC2RBD 94+47+31=172, PD-L1 94+31+34=159, TrkA 94+37=131, TNF-alpha "
            "30+24=54. Changing the filter alone moved the PD-L1 rate from 9.6% over 94 designs to "
            "16.1% over 31 designs."
        ),
        locator="Section S2; Table 1; Table S2",
        review_block=review(SOURCE, PDF_METHOD, HOW),
    ))

    return out
