"""Adaptyv EGFR binder design competition (bioRxiv 10.1101/2025.04.17.648362) and its
round 2 data repository at commit fc91b91ddc367830b755b215dbc69669675ad6a0.

The only source found where many design methods were applied to one target and
measured by a third party on one assay. What it does not give is a per-method hit
rate: the method labels are self-declared entrant free text, the three binding
thresholds in Figure 8 are not defined anywhere in the body, and the repository
states no per-method aggregation. So the printed funnel counts and the printed
per-method outcomes are recorded, and the per-method rates are recorded as a gap.
"""

from common import (AREAS, claim, comparison, evaluation, facets, link, missing, record,
                    result, review, rid)

SOURCE = record(
    rid("source", "adaptyv-preprint"), "source",
    "Crowdsourced Protein Design: Lessons From the Adaptyv EGFR Binder Competition "
    "(Cotet et al., bioRxiv 2025)",
    "Primary source retrieved and hashed for the 2026-10-22 de novo binder design extraction "
    "(issue #176).",
    facets=facets(),
    attributes={
        "url": "https://doi.org/10.1101/2025.04.17.648362",
        "artifact_url": "https://www.biorxiv.org/content/10.1101/2025.04.17.648362v1.full",
        "version": "bioRxiv preprint version 1",
        "retrieved_at": "2026-10-22T12:01:00Z",
        "artifact_sha256": "17039d69ecc37f45f6c402511b8f4497ce631003689fa95ad1ab221f8f787a4f",
        "doi": "10.1101/2025.04.17.648362",
        "publication_status": "preprint",
        "media_type": "text/html",
        "source_locator": "Abstract; Sections 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 4.1, 4.2 and 4.3",
        "retrieval_method": "curl of the bioRxiv full-text HTML rendition, flattened to plain text.",
        "hash_scope": "SHA-256 of one retrieval of a mutable web page. The hash describes that "
                      "retrieval, not a stable artifact.",
        "limitations": [
            "Preprint, not peer reviewed.",
            "Written by the competition organisers, who ran the assay. The designs are the entrants'.",
            "Design methods are self-declared: Section 4.2 states that entrants were asked 'to write a "
            "short summary of their workflow, which we manually curated and categorized into five "
            "design choices'. There is no controlled assignment of methods to designs.",
            "Entrants chose how much effort to spend and how many designs to submit, and Adaptyv "
            "hand-selected 101 of 201 round-1 and 300 of 400 round-2 designs to increase diversity, so "
            "the tested set is not a sample of any method's output.",
            "Figure 8 reports binders 'across the 3 binding thresholds' and the body does not define "
            "those thresholds anywhere.",
            "No conventional comparator arm. EGF and cetuximab were positive controls for the assay, "
            "not a design method evaluated on a set of candidates.",
            "Per-method and per-category hit rates are printed only in Figures 3, 8 and 9 and the 60 "
            "affinities only in Figure 10; the figure values were not read.",
        ],
        "evidence_concerns": [
            {
                "source_id": rid("source", "adaptyv-preprint"),
                "message": (
                    "The paper prints three different round-1 binder rates and two round-2 expression "
                    "rates. Section 2.4 gives round 1 as '2.5% (5/201)' and round 2 as 'a 95% "
                    "expression rate (378 of 400 tested)'; Section 4.1 gives expression as improving "
                    "'from 73% to 94%'; Section 4.2 gives the binder percentage as rising 'from 3% in "
                    "the first round to 13%'. All the printed values are recorded with their locators "
                    "and none is reconciled here."
                ),
                "source_locator": "Sections 2.4, 4.1 and 4.2",
                "artifact_sha256": "17039d69ecc37f45f6c402511b8f4497ce631003689fa95ad1ab221f8f787a4f",
                "review_date": "2026-10-22",
            },
            {
                "source_id": rid("source", "adaptyv-preprint"),
                "message": (
                    "Section 4.1 says Figure 8 shows 'the total number of validated binders across the "
                    "3 binding thresholds' but no section of the paper defines those three thresholds. "
                    "No hit definition is therefore recorded for the Figure 8 counts, and the binding "
                    "protocol's success threshold is left unstated with a reason rather than guessed."
                ),
                "source_locator": "Section 4.1; Figure 8 caption",
                "artifact_sha256": "17039d69ecc37f45f6c402511b8f4497ce631003689fa95ad1ab221f8f787a4f",
                "review_date": "2026-10-22",
            },
        ],
    },
)

SOURCE_REPO = record(
    rid("source", "adaptyv-repo-round2"), "source",
    "Adaptyv EGFR design competition round 2 results repository",
    "Per-design binding affinity and metric tables for round 2 of the Adaptyv EGFR competition, pinned "
    "at one commit for the 2026-10-22 de novo binder design extraction (issue #176).",
    facets=facets(),
    attributes={
        "url": "https://github.com/adaptyvbio/egfr_competition_2",
        "artifact_url": "https://github.com/adaptyvbio/egfr_competition_2/blob/"
                        "fc91b91ddc367830b755b215dbc69669675ad6a0/results/result_summary.csv",
        "version": "commit fc91b91ddc367830b755b215dbc69669675ad6a0",
        "retrieved_at": "2026-10-22T12:02:00Z",
        "artifact_sha256": "b98dd231fa663e10e2768ad0cb7c8b33ba993bc809bd6168390ac87120ce3b7b",
        "publication_status": "official_project_source",
        "licence": "Code Apache-2.0; data ODbL",
        "media_type": "text/csv",
        "artifact_member": "results/result_summary.csv at commit "
                           "fc91b91ddc367830b755b215dbc69669675ad6a0",
        "source_locator": "results/result_summary.csv; README.md Methods",
        "retrieval_method": "git clone of the public repository, checked out at the pinned commit; the "
                            "hash is of results/result_summary.csv at that commit.",
        "code_url": "https://github.com/adaptyvbio/egfr_competition_2",
        "immutable_source_version": "fc91b91ddc367830b755b215dbc69669675ad6a0",
        "limitations": [
            "result_summary.csv has 402 data rows, while the preprint states that 400 designs were "
            "tested in round 2.",
            "The design_models column is the entrants' own free-text declaration (for example 'Custom "
            "PLM'), not a controlled method label.",
            "Neither the README nor the preprint states an aggregation over this file, so no per-method "
            "or per-category rate is computed from it.",
            "The round 1 repository, the raw kinetic curve package, the neutralisation package and the "
            "structure predictions were not retrieved.",
        ],
    },
)

METHOD_CROWD = record(
    rid("method", "adaptyv-crowd-submissions"), "method",
    "Crowdsourced EGFR binder submissions (Adaptyv competition)",
    "The pooled set of EGFR binder designs submitted by competition entrants, each produced by a "
    "workflow the entrant declared and the organisers curated into one of five categories.",
    facets=facets(method_types=["specialist"]),
    source_ids=[SOURCE["id"]],
    attributes={
        "reported_name": "competition submissions",
        "version": "Adaptyv EGFR Binder Design Competition rounds 1 and 2",
        "identity_scope": "A pooled population of designs from many workflows, not a single method. "
                          "Method identity is the entrant's own declaration.",
        "provenance_note": "Created to hold the Adaptyv competition's whole-round funnel counts, which "
                           "are not attributable to any one design method.",
        "source_locator": "Sections 2.2 and 4.2",
    },
)

PIPELINE_CRADLE = record(
    rid("pipeline", "cradle"), "pipeline",
    "Cradle machine-learning-guided lead optimisation",
    "Cradle optimises an existing binder by generating mutations in it and selecting candidates with "
    "machine-learning models trained for the task.",
    facets=facets(method_types=["supervised_machine_learning"]),
    source_ids=[SOURCE["id"]],
    attributes={
        "reported_name": "Cradle",
        "version": "As entered in round 2 of the Adaptyv EGFR competition",
        "access": "Commercial service; not described in detail in this source.",
        "provenance_note": "Created from the Adaptyv competition preprint for the 2026-10-22 binder "
                           "design pass.",
        "source_locator": "Section 3.2",
    },
)

METHOD_CONVENTIONAL = record(
    rid("method", "conventional-binder-discovery"), "method",
    "Conventional binder discovery",
    "Directed evolution, library display selection and grafting from a known complex obtain a new "
    "binder by iterated selection from a library rather than by generating candidate structures.",
    facets=facets(method_types=["conventional_pipeline"]),
    source_ids=[SOURCE["id"]],
    attributes={
        "reported_name": "directed evolution, display selection or grafting",
        "identity_scope": "A family of established pre-machine-learning routes to a binder, named here "
                          "as the comparator the use case needs. No retrieved source runs it as an arm "
                          "on the same targets as a design method.",
        "provenance_note": "Created to name the use case's baseline. Its only same-assay appearance in "
                           "the retrieved evidence is cetuximab, an approved antibody obtained by "
                           "conventional means, run as a positive control in the Adaptyv assay.",
        "source_locator": "Section 2.3 ('Additionally, EGF and Cetuximab were run as positive "
                          "controls'); Section 3.2",
        "missing_metadata": {
            "version": {"reason": "inapplicable",
                        "note": "A family of laboratory methods, not a versioned tool."},
        },
    },
)

CONFIGS = {
    "crowd-r1": record(
        rid("config", "adaptyv", "crowd-r1"), "configuration",
        "Adaptyv EGFR competition round 1 selected submissions",
        "The 201 round-1 submissions Adaptyv selected for testing: the top 100 by interface predicted "
        "aligned error from AlphaFold2-Multimer plus 101 chosen by hand from 726 submissions.",
        facets=facets(method_types=["specialist"]),
        source_ids=[SOURCE["id"]],
        links=[link("configuration_of", METHOD_CROWD["id"])],
        attributes={
            "reported_name": "R1",
            "version": "Adaptyv EGFR Binder Design Competition round 1",
            "parameters": "726 submissions from about 50 designers; sequences under 200 residues, at "
                          "least 10 residues from a published binder, natural amino acids and single "
                          "chain; ranked by interface predicted aligned error (iPAE) from "
                          "AlphaFold2-Multimer",
            "selection": "Top 100 by iPAE plus 101 selected by hand, from 726 submissions.",
            "limitations": [
                "Half the tested set was hand-picked by the organisers to increase diversity across "
                "design methods, so it is not a sample of any method's output.",
            ],
            "access_reuse": "Entrant designs, tested by a third-party laboratory.",
            "method_role": "pooled submissions",
            "foundation_model_eligible": False,
            "source_locator": "Sections 2.1, 2.2 and 2.4",
        },
    ),
    "crowd-r2": record(
        rid("config", "adaptyv", "crowd-r2"), "configuration",
        "Adaptyv EGFR competition round 2 selected submissions",
        "The 400 round-2 submissions Adaptyv selected for testing: the top 100 by a Borda count of "
        "ESM2 pseudo-log-likelihood, iPAE and ipTM plus 300 chosen by hand from 1,131 submissions.",
        facets=facets(method_types=["specialist"]),
        source_ids=[SOURCE["id"]],
        links=[link("configuration_of", METHOD_CROWD["id"])],
        attributes={
            "reported_name": "R2",
            "version": "Adaptyv EGFR Binder Design Competition round 2",
            "parameters": "1,131 submissions from 130 participants; sequences under 250 residues, at "
                          "least 10 residues from a published binder, natural amino acids and single "
                          "chain; ranked by a Borda count aggregate of ESM2 pseudo-log-likelihood (not "
                          "length-normalised), iPAE and ipTM",
            "selection": "Top 100 by the Borda count plus 300 selected manually, from 1,131 "
                         "submissions. Each designer had at least one submission validated.",
            "limitations": [
                "Three quarters of the tested set was hand-picked by the organisers, so it is not a "
                "sample of any method's output.",
                "The paper notes the unnormalised ESM2 likelihood 'was biased towards smaller designs' "
                "and that either ranking metric 'could be biased against (or for) certain de novo or "
                "underrepresented folds'.",
            ],
            "access_reuse": "Entrant designs, tested by a third-party laboratory.",
            "method_role": "pooled submissions",
            "foundation_model_eligible": False,
            "source_locator": "Sections 2.1, 2.2 and 2.4",
        },
    ),
    "bindcraft-r1": record(
        rid("config", "adaptyv", "bindcraft-r1"), "configuration",
        "BindCraft default settings as entered in Adaptyv round 1",
        "BindCraft run by its own authors with the published default settings against the beta-sheeted "
        "interface of EGFR, with the top-scoring designs selected by AlphaFold2 ipTM.",
        facets=facets(method_types=["specialist"]),
        source_ids=[SOURCE["id"]],
        links=[link("configuration_of", rid("pipeline", "bindcraft"))],
        attributes={
            "reported_name": "BindCraft",
            "version": "As entered in Adaptyv EGFR competition round 1",
            "parameters": "Default settings, targeting the beta-sheeted interface of EGFR; top-scoring "
                          "binders by AlphaFold2 ipTM, mostly helical",
            "selection": "Five designs selected for evaluation by the authors.",
            "access_reuse": "Entered by the BindCraft authors; tested by Adaptyv.",
            "method_role": "design",
            "foundation_model_eligible": False,
            "source_locator": "Section 3.1",
        },
    ),
    "bindcraft-r2": record(
        rid("config", "adaptyv", "bindcraft-r2-beta"), "configuration",
        "BindCraft with helical loss -2.0 as entered in Adaptyv round 2",
        "BindCraft run with the helicity loss set to -2.0 instead of the default -0.3, so that only "
        "beta-sheeted designs from the same design campaign were submitted.",
        facets=facets(method_types=["specialist"]),
        source_ids=[SOURCE["id"]],
        links=[link("configuration_of", rid("pipeline", "bindcraft"))],
        attributes={
            "reported_name": "BindCraft",
            "version": "As entered in Adaptyv EGFR competition round 2",
            "parameters": "Helical loss set to -2.0 (default -0.3), yielding beta-sheeted designs from "
                          "the same design campaign as the round 1 entry",
            "selection": "Ten beta-sheeted designs from the authors' submission were tested.",
            "access_reuse": "Entered by the BindCraft authors; tested by Adaptyv.",
            "method_role": "design",
            "foundation_model_eligible": False,
            "source_locator": "Section 3.1",
        },
    ),
    "bindcraft-gb1": record(
        rid("config", "adaptyv", "bindcraft-gb1-composite"), "configuration",
        "Paired BindCraft designs joined by custom linkers with a GB1 solubility tag",
        "Composite multi-domain submissions, each joining two BindCraft designs and the GB1 "
        "solubility-enhancement tag with custom disordered linkers.",
        facets=facets(method_types=["specialist"]),
        source_ids=[SOURCE["id"]],
        links=[link("configuration_of", rid("pipeline", "bindcraft"))],
        attributes={
            "reported_name": "BindCraft",
            "version": "As entered in Adaptyv EGFR competition round 2 by a third-party participant",
            "parameters": "Two BindCraft designs per submission plus the GB1 solubility-enhancement "
                          "tag, connected by custom disordered linkers",
            "selection": "Five composite designs were tested in round 2.",
            "access_reuse": "Entered by a participant, not by the BindCraft authors.",
            "method_role": "design",
            "foundation_model_eligible": False,
            "source_locator": "Section 3.1, final paragraph",
        },
    ),
    "cradle-r2": record(
        rid("config", "adaptyv", "cradle-r2"), "configuration",
        "Cradle lead optimisation of a cetuximab single-chain variable fragment",
        "Cradle's round 2 entry: cetuximab reformatted as a single-chain variable fragment with a "
        "glycine-serine linker, then mutated in the framework regions under machine-learning-guided "
        "selection with the complementarity-determining regions preserved.",
        facets=facets(method_types=["supervised_machine_learning"]),
        source_ids=[SOURCE["id"]],
        links=[link("configuration_of", PIPELINE_CRADLE["id"])],
        attributes={
            "reported_name": "Cradle",
            "version": "As entered in Adaptyv EGFR competition round 2",
            "parameters": "Cetuximab reformatted as an scFv with a glycine-serine linker; mutations "
                          "generated in the framework regions only, with the CDRs preserved",
            "selection": "Not stated.",
            "access_reuse": "Commercial entry; tested by Adaptyv.",
            "method_role": "lead optimisation",
            "foundation_model_eligible": False,
            "source_locator": "Section 3.2",
            "missing_metadata": {
                "parent_identity_review": {
                    "reason": "unreported",
                    "note": "The source does not describe which models Cradle used.",
                },
            },
        },
    ),
}

DATASETS = {
    "r1": record(
        rid("data", "adaptyv", "egfr-r1"), "dataset",
        "Adaptyv EGFR competition round 1 tested designs",
        "The 201 round-1 designs Adaptyv expressed and assayed against EGFR, selected from 726 "
        "submissions.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "reported_name": "R1",
            "version": "Adaptyv EGFR Binder Design Competition round 1, results revealed 2024",
            "assay": "Cell-free expression, label-free expression quantification, then multi-cycle "
                     "kinetic BLI against EGFR at 1000 nM to 10 nM, in duplicate",
            "total": 201,
            "population": "201 selected designs from 726 submissions by about 50 designers",
            "source_locator": "Sections 2.2 and 2.4",
        },
    ),
    "r2": record(
        rid("data", "adaptyv", "egfr-r2"), "dataset",
        "Adaptyv EGFR competition round 2 tested designs",
        "The 400 round-2 designs Adaptyv expressed and assayed against EGFR, selected from 1,131 "
        "submissions, with per-design results published in the round 2 repository.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_REPO["id"]],
        attributes={
            "reported_name": "R2",
            "version": "Adaptyv EGFR Binder Design Competition round 2, results revealed December 2024",
            "assay": "Cell-free expression, label-free expression quantification, then multi-cycle "
                     "kinetic BLI against EGFR at 1000 nM to 10 nM, in duplicate",
            "total": 400,
            "population": "400 selected designs from 1,131 submissions by 130 participants",
            "repository": "https://github.com/adaptyvbio/egfr_competition_2",
            "access": "Data under ODbL; per-design rows in results/result_summary.csv at commit "
                      "fc91b91ddc367830b755b215dbc69669675ad6a0",
            "source_locator": "Sections 2.2 and 2.4; results/result_summary.csv",
            "scope_note": "results/result_summary.csv holds 402 data rows against the 400 tested "
                          "designs the paper states.",
        },
    ),
    "both": record(
        rid("data", "adaptyv", "egfr-both-rounds"), "dataset",
        "Adaptyv EGFR competition, both rounds",
        "The 601 designs Adaptyv expressed and assayed against EGFR across both rounds, from 1,857 "
        "submissions by 159 unique participants.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "reported_name": "R1 and R2",
            "version": "Adaptyv EGFR Binder Design Competition, rounds 1 and 2",
            "assay": "Cell-free expression then multi-cycle kinetic BLI against EGFR, in duplicate",
            "total": 601,
            "population": "601 selected designs from 1,857 submissions by 159 unique participants",
            "source_locator": "Abstract; Section 2.4",
        },
    ),
}

BLI_LIMITS = [
    "Third-party assay: Adaptyv expressed and measured the designs, so the measurement is independent "
    "of the design methods. The organisers wrote the paper.",
    "No hit definition is printed. Section 4.1 refers to 'the 3 binding thresholds' in Figure 8 and no "
    "section of the paper defines them.",
    "The tested set is not a sample of any method's output: half the round-1 and three quarters of the "
    "round-2 tested designs were hand-picked by the organisers for diversity, and entrants chose how "
    "many designs to submit and how much effort to spend.",
    "Design methods are the entrants' own declarations, curated by the organisers into five categories.",
    "Sequences yielding under 0.02 micrograms per millilitre of protein were excluded before "
    "characterisation, so the binding denominator is the expressed set for some statements and the "
    "selected set for others.",
    "No conventional comparator arm. EGF and cetuximab were positive controls.",
    "No uncertainty is printed for any rate.",
]

PROTOCOLS = {
    "binding": record(
        rid("protocol", "adaptyv", "bli-binding"), "protocol",
        "Adaptyv EGFR competition BLI binding screen",
        "Share of selected competition designs confirmed as binders to EGFR by Adaptyv's automated "
        "cell-free expression and biolayer interferometry pipeline.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "Submitted sequences are reverse-translated and codon-optimised, expressed in a "
                "cell-free system in at least two batches, and quantified by a label-free assay. "
                "Sequences yielding less than 0.02 micrograms per millilitre are excluded. Expressed "
                "ligands are immobilised by tag-specific chemistry and EGFR is flowed over the probe at "
                "1000 nM to 10 nM in a multi-cycle kinetic assay, in duplicate, in HBS-T with 0.5% BSA "
                "at 25 degrees Celsius. Signals are baseline-corrected and fitted with a 1:1 binding "
                "model; where the maximum signal is below the quantifiable threshold or the kinetics "
                "are too fast, equilibrium analysis is used instead. A minimum of two replicates was "
                "run for each design, and EGF and cetuximab were run as positive controls."
            ),
            "version": "bioRxiv v1 Section 2.3; round 2 repository README Methods at commit "
                       "fc91b91ddc367830b755b215dbc69669675ad6a0",
            "metric": "hit-rate",
            "metric_direction": "higher",
            "metric_qualifier": "designs confirmed as binders to EGFR by BLI, out of designs selected "
                                "for testing",
            "unit": "percent",
            "control": "EGF and cetuximab as positive controls; cetuximab measured 9.94 nM in this "
                       "assay.",
            "selection_bias": "Half the round-1 and three quarters of the round-2 tested designs were "
                              "hand-picked by the organisers for diversity.",
            "source_locator": "Sections 2.3 and 2.4; round 2 repository README, 'Experimental "
                              "Workflow'",
            "limitations": BLI_LIMITS,
            "missing_metadata": {
                "success_threshold": {
                    "reason": "unreported",
                    "note": "Section 4.1 refers to Figure 8 reporting binders 'across the 3 binding "
                            "thresholds' and the body never defines them. No threshold is recorded and "
                            "none is inferred.",
                },
            },
        },
    ),
    "expression": record(
        rid("protocol", "adaptyv", "expression"), "protocol",
        "Adaptyv EGFR competition cell-free expression rate",
        "Share of selected competition designs that expressed in Adaptyv's cell-free system.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "Submitted sequences are reverse-translated, codon-optimised and expressed in a "
                "cell-free system over at least two batches, with some sequences tested up to four "
                "times. Expression success is assessed by a label-free quantification assay; sequences "
                "yielding less than 0.02 micrograms per millilitre are excluded from further "
                "characterisation."
            ),
            "version": "bioRxiv v1 Sections 2.3 and 2.4",
            "metric": "proportion",
            "metric_direction": "higher",
            "metric_qualifier": "designs that expressed above the 0.02 microgram per millilitre "
                                "threshold, out of designs selected for testing",
            "unit": "percent",
            "source_locator": "Sections 2.4 and 4.1; round 2 repository README, 'Protein Synthesis'",
            "limitations": BLI_LIMITS + [
                "Section 2.4 gives the round 2 expression rate as 95% (378 of 400) and Section 4.1 "
                "gives it as 94%.",
            ],
        },
    ),
    "affinity": record(
        rid("protocol", "adaptyv", "bli-affinity"), "protocol",
        "Adaptyv EGFR competition BLI affinity",
        "Dissociation constant of a competition design for EGFR, fitted from multi-cycle kinetic BLI.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_REPO["id"]],
        attributes={
            "protocol": (
                "Multi-cycle kinetic BLI against EGFR from 1000 nM to 10 nM in duplicate, "
                "baseline-corrected and fitted with a 1:1 binding model per replicate; equilibrium "
                "analysis where the signal is below the quantifiable threshold or the kinetics are too "
                "fast. Each experimental replicate is analysed independently."
            ),
            "version": "bioRxiv v1 Section 2.3; round 2 repository README Methods at commit "
                       "fc91b91ddc367830b755b215dbc69669675ad6a0",
            "metric": "dissociation-constant",
            "metric_direction": "lower",
            "metric_qualifier": "KD for EGFR by multi-cycle kinetic BLI, 1:1 fit",
            "unit": "nanomolar",
            "control": "Cetuximab positive control measured 9.94 nM in this assay.",
            "source_locator": "Section 2.3; Sections 3.1, 3.2 and 4.3; results/result_summary.csv",
            "limitations": [
                "Third-party measurement, independent of the design methods.",
                "Figure 10 reports the distribution over all 60 binders; the figure was not read. Only "
                "the affinities printed in the prose are recorded.",
                "Section 4.3 states that a Kruskal-Wallis test found no statistically significant "
                "difference in median affinity between the two rounds.",
                "The Cradle entry is an optimisation of cetuximab, so its affinity is relative to an "
                "existing antibody rather than a de novo design.",
            ],
        },
    ),
}

HTML_METHOD = ["transcription"]
HOW = ("Transcribed by hand from the plain-text flattening of the pinned bioRxiv full-text HTML. Each "
       "value was located in the body prose and the surrounding sentence is quoted in the source "
       "locator. Figures 3, 8, 9 and 10 were not read.")
REPO_METHOD = ["deterministic-table-parse", "transcription"]
REPO_HOW = ("Read from results/result_summary.csv at the pinned commit with Python's csv module. The "
            "Cradle affinity printed in Section 3.2 as 1.21 nM matches the row "
            "'round1zeroshot.K5Q_N70S_K71R_N73T_S87T_N88D_R179K_K183R_E213D_S214P' (username Cradle), "
            "whose kd column holds 1.2071528940932701e-09 molar.")


def build():
    out = [SOURCE, SOURCE_REPO, METHOD_CROWD, PIPELINE_CRADLE, METHOD_CONVENTIONAL]
    out += list(CONFIGS.values())
    out += list(DATASETS.values())
    out += list(PROTOCOLS.values())
    rev = review(SOURCE, HTML_METHOD, HOW)
    rev_repo = review(SOURCE_REPO, REPO_METHOD, REPO_HOW)

    def make_eval(ev_id, name, system, protocol, data, population, budget, locator,
                  metric_impl, attrs=None, extra_missing=None):
        m = {
            "comparison.split": {"reason": "inapplicable",
                                 "note": "A design competition, not a train/test split."},
            "comparison.adaptation": {"reason": "inapplicable",
                                      "note": "No adaptation step; designs were submitted as they were "
                                              "generated."},
        }
        if extra_missing:
            m.update(extra_missing)
        out.append(evaluation(
            ev_id, name,
            "Third-party measurement of entrant designs, transcribed from the pinned source; not "
            "reproduced.",
            source=SOURCE, system=system, assessment=protocol, data=data,
            origin="independent_paper", version="bioRxiv v1",
            comparison=comparison(
                protocol,
                dataset_version=DATASETS["r2"]["attributes"]["version"] if data == DATASETS["r2"]["id"]
                                else DATASETS["r1"]["attributes"]["version"] if data == DATASETS["r1"]["id"]
                                else DATASETS["both"]["attributes"]["version"],
                population=population,
                inputs="EGFR structure; entrants chose their own inputs and workflow",
                metric_implementation=metric_impl,
                aggregation="Over the designs tested in the stated round",
                budget=budget,
            ),
            locator=locator,
            attrs=attrs or {},
            missing=m,
        ))

    # Round-level funnel and rates.
    make_eval(
        rid("eval", "adaptyv", "r1", "binding"),
        "Adaptyv EGFR competition round 1 binding rate",
        CONFIGS["crowd-r1"]["id"], PROTOCOLS["binding"]["id"], DATASETS["r1"]["id"],
        "201 selected designs from 726 submissions",
        "201 designs expressed and assayed",
        "Section 2.4",
        "Share of selected designs confirmed as binders by BLI",
        attrs={"denominator": 201, "endpoint": "BLI-confirmed binding to EGFR",
               "conventional_baseline": "None. EGF and cetuximab were positive controls."},
    )
    out.append(result(
        rid("result", "adaptyv", "r1", "hitrate"),
        "Adaptyv EGFR competition round 1 binder rate",
        "Third-party measured value transcribed from the pinned source. Not reproduced.",
        source=SOURCE, evaluation_id=rid("eval", "adaptyv", "r1", "binding"),
        printed="2.5% (5/201)", numeric="2.5",
        metric="hit-rate", direction="higher", unit="percent",
        qualifier="novel binders confirmed by BLI, out of designs selected for testing; excludes two "
                  "binders later disqualified for similarity to an existing binder",
        unit_detail="percent of designs selected for testing",
        numerator=5, denominator=201,
        denominator_note="201 designs selected for testing, of which 146 expressed. The printed rate "
                         "uses 201, the selected set, not 146.",
        locator="Section 2.4: 'previous work on de novo binders to EGFR achieved an 0.01% hit rate "
                "versus the 2.5% (5/201) we had observed in R1'",
        review_block=rev,
        missing=missing(uncertainty=("unreported", "No interval is printed.")),
    ))
    out.append(result(
        rid("result", "adaptyv", "r1", "binders"),
        "Adaptyv EGFR competition round 1 novel binders",
        "Third-party measured count transcribed from the pinned source. Not reproduced.",
        source=SOURCE, evaluation_id=rid("eval", "adaptyv", "r1", "binding"),
        printed="5 novel binders (+2 disqualified binders which slipped through the similarity check to "
                "existing binders initially)",
        numeric="5", metric="count", direction="higher", unit="count",
        qualifier="novel binders confirmed by BLI; two further binders were disqualified for similarity "
                  "to an existing EGFR binder",
        unit_detail="designs",
        numerator=5, denominator=201,
        denominator_note="201 designs selected for testing; 146 expressed.",
        locator="Section 2.4: 'Out of these designs, 146 expressed with 5 novel binders (+2 "
                "disqualified binders which slipped through the similarity check to existing binders "
                "initially).'",
        review_block=rev,
        missing=missing(uncertainty=("inapplicable", "An exact count.")),
    ))

    make_eval(
        rid("eval", "adaptyv", "r1", "expression"),
        "Adaptyv EGFR competition round 1 expression rate",
        CONFIGS["crowd-r1"]["id"], PROTOCOLS["expression"]["id"], DATASETS["r1"]["id"],
        "201 selected designs from 726 submissions",
        "201 designs expressed",
        "Section 2.4",
        "Share of selected designs expressing above the 0.02 microgram per millilitre threshold",
        attrs={"denominator": 201, "endpoint": "cell-free expression above threshold"},
    )
    out.append(result(
        rid("result", "adaptyv", "r1", "expression-rate"),
        "Adaptyv EGFR competition round 1 expression rate",
        "Third-party measured value transcribed from the pinned source. Not reproduced.",
        source=SOURCE, evaluation_id=rid("eval", "adaptyv", "r1", "expression"),
        printed="73%", numeric="73",
        metric="proportion", direction="higher", unit="percent",
        qualifier="designs expressing above the 0.02 microgram per millilitre threshold, out of designs "
                  "selected for testing",
        unit_detail="percent of designs selected for testing",
        numerator=146, denominator=201,
        denominator_note="146 of 201 expressed, from the preceding sentence.",
        locator="Section 2.4: 'The expression rate of 73% was about on par for the design methods "
                "commonly in the field'",
        review_block=rev,
        missing=missing(uncertainty=("unreported", "No interval is printed.")),
    ))

    make_eval(
        rid("eval", "adaptyv", "r2", "binding"),
        "Adaptyv EGFR competition round 2 binding rate",
        CONFIGS["crowd-r2"]["id"], PROTOCOLS["binding"]["id"], DATASETS["r2"]["id"],
        "400 selected designs from 1,131 submissions",
        "400 designs expressed and assayed",
        "Sections 2.4 and 4.2",
        "Share of selected designs confirmed as binders by BLI",
        attrs={"denominator": 400, "endpoint": "BLI-confirmed binding to EGFR",
               "conventional_baseline": "None. EGF and cetuximab were positive controls."},
    )
    out.append(result(
        rid("result", "adaptyv", "r2", "binders"),
        "Adaptyv EGFR competition round 2 confirmed binders",
        "Third-party measured count transcribed from the pinned source. Not reproduced.",
        source=SOURCE, evaluation_id=rid("eval", "adaptyv", "r2", "binding"),
        printed="53 confirmed binders", numeric="53",
        metric="count", direction="higher", unit="count",
        qualifier="designs confirmed as binders by BLI",
        unit_detail="designs",
        numerator=53, denominator=400,
        denominator_note="400 designs tested, of which 378 expressed. The paper prints the count, not a "
                         "rate, in this sentence.",
        locator="Section 2.4: 'R2 saw a 95% expression rate (378 of 400 tested) as well as a much "
                "higher binding rate with 53 confirmed binders'",
        review_block=rev,
        missing=missing(uncertainty=("inapplicable", "An exact count.")),
    ))
    out.append(result(
        rid("result", "adaptyv", "r2", "hitrate-section-4-2"),
        "Adaptyv EGFR competition round 2 binder percentage (Section 4.2)",
        "Third-party measured value transcribed from the pinned source. Not reproduced.",
        source=SOURCE, evaluation_id=rid("eval", "adaptyv", "r2", "binding"),
        printed="13%", numeric="13",
        metric="hit-rate", direction="higher", unit="percent",
        qualifier="designs confirmed as binders by BLI, out of designs selected for testing; the "
                  "sentence gives round 1 as 3%, which does not reconcile with the 2.5% (5/201) in "
                  "Section 2.4",
        unit_detail="percent of designs selected for testing",
        denominator=400,
        denominator_note="400 designs tested. The sentence points at Figure 8, which reports binders "
                         "across three undefined binding thresholds.",
        locator="Section 4.2: 'the most exciting improvement has been in the percentage of successful "
                "binders to EGFR, from 3% in the first round to 13% (Figure 8)'",
        review_block=rev,
        missing=missing(
            uncertainty=("unreported", "No interval is printed."),
            numerator=("conflicting",
                       "13% of 400 is 52 against the 53 confirmed binders stated in Section 2.4, and "
                       "the sentence points at a figure with three undefined thresholds."),
        ),
    ))
    out.append(result(
        rid("result", "adaptyv", "r1", "hitrate-section-4-2"),
        "Adaptyv EGFR competition round 1 binder percentage (Section 4.2)",
        "Third-party measured value transcribed from the pinned source. Not reproduced. It does not "
        "reconcile with the 2.5% printed in Section 2.4.",
        source=SOURCE, evaluation_id=rid("eval", "adaptyv", "r1", "binding"),
        printed="3%", numeric="3",
        metric="hit-rate", direction="higher", unit="percent",
        qualifier="designs confirmed as binders by BLI, out of designs selected for testing, as stated "
                  "in Section 4.2; Section 2.4 prints 2.5% (5/201) for the same round",
        unit_detail="percent of designs selected for testing",
        denominator=201,
        denominator_note="201 designs selected for testing. The sentence points at Figure 8, which "
                         "reports binders across three undefined binding thresholds.",
        locator="Section 4.2: 'from 3% in the first round to 13% (Figure 8)'",
        review_block=rev,
        extra={"source_discrepancy": "Section 2.4 prints 2.5% (5/201) for round 1 and Section 4.2 "
                                     "prints 3%. Both are recorded."},
        missing=missing(
            uncertainty=("unreported", "No interval is printed."),
            numerator=("conflicting", "3% of 201 is 6 against the 5 novel binders in Section 2.4."),
        ),
    ))

    make_eval(
        rid("eval", "adaptyv", "r2", "expression"),
        "Adaptyv EGFR competition round 2 expression rate",
        CONFIGS["crowd-r2"]["id"], PROTOCOLS["expression"]["id"], DATASETS["r2"]["id"],
        "400 selected designs from 1,131 submissions",
        "400 designs expressed",
        "Sections 2.4 and 4.1",
        "Share of selected designs expressing above the 0.02 microgram per millilitre threshold",
        attrs={"denominator": 400, "endpoint": "cell-free expression above threshold"},
    )
    for tag, printed, numeric, locator, note in [
        ("95", "95%", "95",
         "Section 2.4: 'R2 saw a 95% expression rate (378 of 400 tested)'",
         "Section 4.1 prints 94% for the same quantity."),
        ("94", "94%", "94",
         "Section 4.1: 'We observed an improvement in the number of designs expressed, from 73% to 94%'",
         "Section 2.4 prints 95% (378 of 400) for the same quantity. 378 of 400 is 94.5%."),
    ]:
        out.append(result(
            rid("result", "adaptyv", "r2", "expression-rate", tag),
            f"Adaptyv EGFR competition round 2 expression rate ({printed})",
            "Third-party measured value transcribed from the pinned source. Not reproduced.",
            source=SOURCE, evaluation_id=rid("eval", "adaptyv", "r2", "expression"),
            printed=printed, numeric=numeric,
            metric="proportion", direction="higher", unit="percent",
            qualifier="designs expressing above the 0.02 microgram per millilitre threshold, out of "
                      "designs selected for testing",
            unit_detail="percent of designs selected for testing",
            numerator=378, denominator=400,
            denominator_note="378 of 400 expressed, printed in Section 2.4.",
            locator=locator, review_block=rev,
            extra={"source_discrepancy": note},
            missing=missing(uncertainty=("unreported", "No interval is printed.")),
        ))

    # Both rounds together.
    make_eval(
        rid("eval", "adaptyv", "both", "binding"),
        "Adaptyv EGFR competition total binders across both rounds",
        METHOD_CROWD["id"], PROTOCOLS["binding"]["id"], DATASETS["both"]["id"],
        "601 selected designs from 1,857 submissions by 159 unique participants",
        "601 designs expressed and assayed",
        "Abstract; Sections 2.4 and 4.2",
        "Count of designs confirmed as binders by BLI across both rounds",
        attrs={"denominator": 601, "endpoint": "BLI-confirmed binding to EGFR",
               "conventional_baseline": "None. EGF and cetuximab were positive controls."},
    )
    for tag, printed, numeric, qualifier, locator, extra in [
        ("total", "60 binders", "60", "designs confirmed as binders by BLI across both rounds",
         "Section 4.2: 'In total, we have amassed 60 binders, with 4 of those as strong binders (in the "
         "tens of nM range).'", None),
        ("strong", "4", "4",
         "binders the paper calls strong, in the tens of nanomolar range",
         "Section 4.2: 'with 4 of those as strong binders (in the tens of nM range)'",
         "The paper does not define 'strong binder' beyond 'in the tens of nM range'."),
        ("better-than-cetuximab", "2", "2",
         "binders with better affinity for EGFR than the cetuximab positive control",
         "Section 4.2: 'Out of these, 2 had better binding affinities than the Cetuximab control in the "
         "nanomolar range.'", None),
    ]:
        out.append(result(
            rid("result", "adaptyv", "both", "binders", tag),
            f"Adaptyv EGFR competition, {qualifier}",
            "Third-party measured count transcribed from the pinned source. Not reproduced.",
            source=SOURCE, evaluation_id=rid("eval", "adaptyv", "both", "binding"),
            printed=printed, numeric=numeric,
            metric="count", direction="higher", unit="count",
            qualifier=qualifier, unit_detail="designs",
            denominator=601,
            denominator_note="601 designs selected and characterised across both rounds.",
            locator=locator, review_block=rev,
            extra={"scope_note": extra} if extra else None,
            missing=missing(uncertainty=("inapplicable", "An exact count.")),
        ))

    # Per-method outcomes printed in the prose.
    per_method = [
        ("bindcraft-r1", CONFIGS["bindcraft-r1"]["id"], "r1", 5,
         "BindCraft in Adaptyv round 1",
         [("expressed", "count", "Four of those showed high expression rates", "4",
           "designs with high expression", "count", "designs", 4, 5,
           "Section 3.1: 'five were selected for evaluation. Four of those showed high expression rates'"),
          ("kd", "dissociation-constant", "491 nM", "491",
           "best KD for EGFR by BLI among the round 1 BindCraft entries; the strongest binding affinity "
           "in round 1", "nanomolar", None, None, 5,
           "Section 3.1: 'one exhibited the strongest binding affinity in this round of the competition "
           "at 491 nM'")]),
        ("bindcraft-r2", CONFIGS["bindcraft-r2"]["id"], "r2", 10,
         "BindCraft with helical loss -2.0 in Adaptyv round 2",
         [("expressed", "count", "all ten showed high expression rates", "10",
           "designs with high expression", "count", "designs", 10, 10,
           "Section 3.1: 'Ten out of the author's submitted beta sheeted designs were tested and - given "
           "the lower overall expression rate of the competition in R1 - surprisingly all ten showed "
           "high expression rates'"),
          ("kd", "dissociation-constant", "82 nM", "82",
           "best KD for EGFR by BLI among the round 2 BindCraft entries; the tightest binding de novo "
           "binder in round 2", "nanomolar", None, None, 10,
           "Section 3.1: 'One of those designs bound with 82 nM affinity to the EGFR target, making it "
           "the tightest binding de novo binder in R2'")]),
        ("bindcraft-gb1", CONFIGS["bindcraft-gb1"]["id"], "r2", 5,
         "Paired BindCraft designs with a GB1 tag in Adaptyv round 2",
         [("expressed", "count", "all five showed high expression", "5",
           "designs with high expression", "count", "designs", 5, 5,
           "Section 3.1: 'Five of these composite designs were tested in R2; all five showed high "
           "expression but did not bind.'"),
          ("binders", "count", "did not bind", "0",
           "designs confirmed as binders by BLI", "count", "designs", 0, 5,
           "Section 3.1: 'Five of these composite designs were tested in R2; all five showed high "
           "expression but did not bind.'")]),
        ("cradle-r2", CONFIGS["cradle-r2"]["id"], "r2", None,
         "Cradle lead optimisation in Adaptyv round 2",
         [("kd", "dissociation-constant", "1.21 nM", "1.21",
           "KD for EGFR by BLI of the overall competition winner, an optimised cetuximab scFv",
           "nanomolar", None, None, None,
           "Section 3.2: 'The overall winner of the competition (by binding affinity), and the winner of "
           "R2, was the ML-guided lead optimization strategy of Cradle, with a binding affinity of 1.21 "
           "nM'")]),
    ]
    for cfg_tag, system, round_key, tested, label, rows in per_method:
        for (row_tag, metric, printed, numeric, qualifier, unit, unit_detail, numerator,
             denominator, locator) in rows:
            proto = (PROTOCOLS["affinity"] if metric == "dissociation-constant"
                     else PROTOCOLS["expression"] if row_tag == "expressed"
                     else PROTOCOLS["binding"])
            ev_id = rid("eval", "adaptyv", cfg_tag, proto["id"].rsplit("-", 1)[-1])
            if not any(r["id"] == ev_id for r in out):
                make_eval(
                    ev_id, f"{label}: {proto['name']}",
                    system, proto["id"], DATASETS[round_key]["id"],
                    f"{tested} designs tested" if tested else None,
                    f"{tested} designs tested" if tested else None,
                    locator,
                    qualifier,
                    attrs={"denominator": tested} if tested else {},
                    extra_missing=(None if tested else {
                        "comparison.population": {
                            "reason": "unreported",
                            "note": "The source does not say how many Cradle designs were tested.",
                        },
                        "comparison.budget": {
                            "reason": "unreported",
                            "note": "The source does not say how many Cradle designs were tested.",
                        },
                    }),
                )
            out.append(result(
                rid("result", "adaptyv", cfg_tag, row_tag),
                f"{label}: {qualifier}",
                "Third-party measured value transcribed from the pinned source. Not reproduced.",
                source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
                metric=metric, direction="lower" if metric == "dissociation-constant" else "higher",
                unit=unit, qualifier=qualifier, unit_detail=unit_detail,
                numerator=numerator, denominator=denominator,
                denominator_note=(f"{denominator} designs tested." if denominator else None),
                locator=locator,
                review_block=(rev_repo if cfg_tag == "cradle-r2" and row_tag == "kd" else rev),
                source_ids=([SOURCE["id"], SOURCE_REPO["id"]]
                            if cfg_tag == "cradle-r2" and row_tag == "kd" else None),
                extra=({"printed_value_basis": "The count is stated in words; zero binders here is a "
                                               "measured zero, not a missing value."}
                       if printed == "did not bind" else None),
                missing=missing(
                    uncertainty=("inapplicable", "An exact count.") if metric == "count"
                    else ("unreported", "No interval is printed for this value in the prose; the "
                                        "repository records per-replicate fits."),
                ),
            ))

    out.append(claim(
        rid("claim", "adaptyv", "bindcraft-share-of-de-novo-binders"),
        "Seven of the eight de novo binders in Adaptyv round 2 were designed with BindCraft",
        "The paper states that seven of the eight de novo binders found in round 2 came from BindCraft, "
        "even though most de novo submissions came from RFdiffusion pipelines. This is a per-method "
        "outcome printed in the prose, not a hit rate: the denominators per method are not printed.",
        source=SOURCE, subject=rid("pipeline", "bindcraft"), field="share_of_de_novo_binders",
        value=(
            "Section 3.1, verbatim: 'Overall, 7 out of 8 de novo binders in the second round were "
            "designed using BindCraft, despite most de novo designs in the competition originating from "
            "the RFDiffusion pipeline.' The paper does not print how many RFdiffusion designs were "
            "tested, so no RFdiffusion hit rate can be read from this source. Section 3.1 also states "
            "that 'the best R2 BindCraft design does not have any significantly similar structural hits "
            "in either the Protein Data Bank (PDB) or AlphaFold Protein Structure Database (AFDB)'."
        ),
        locator="Section 3.1",
        review_block=rev,
    ))

    out.append(claim(
        rid("claim", "adaptyv", "cetuximab-positive-control"),
        "Cetuximab, obtained by conventional means, measured 9.94 nM in the same assay",
        "The Adaptyv assay ran EGF and cetuximab as positive controls, and cetuximab measured 9.94 nM. "
        "This is the only same-assay measurement of a conventionally obtained binder in any source this "
        "pass retrieved. It is a control for assay validity, not a design-method arm: there is no "
        "candidate set and no denominator behind it.",
        source=SOURCE, subject=METHOD_CONVENTIONAL["id"], field="same_assay_reference_measurement",
        value=(
            "Section 2.3: 'Additionally, EGF and Cetuximab were run as positive controls.' Section 3.2: "
            "'Cetuximab was also used as a positive control in the competition (9.94 nM), allowing for "
            "the calculation that this represents an 8.2 x improvement.' Section 4.3: 'Two R2 binders "
            "have KD values on par or better than Cetuximab.' Cetuximab is an approved therapeutic "
            "antibody obtained by conventional antibody discovery, so its 9.94 nM in this assay is a "
            "reference point for what a conventional binder achieves on EGFR, measured on the same "
            "instrument as the designs. It is not evidence about the hit rate of conventional methods, "
            "because no library selection campaign was run and no candidate set was tested."
        ),
        locator="Sections 2.3, 3.2 and 4.3",
        review_block=rev,
    ))

    out.append(claim(
        rid("claim", "adaptyv", "per-method-rates-not-extractable"),
        "Per-method hit rates cannot be read from the Adaptyv round 2 data",
        "The round 2 repository publishes one row per tested design with a binding flag, an affinity and "
        "the entrant's declared design models, but neither the repository nor the preprint states an "
        "aggregation over those rows, the method labels are free text, and the three binding thresholds "
        "behind the figure counts are never defined. No per-method rate is computed from this file.",
        source=SOURCE_REPO, subject=DATASETS["r2"]["id"], field="per_method_aggregation_not_stated",
        value=(
            "results/result_summary.csv at commit fc91b91ddc367830b755b215dbc69669675ad6a0 has 402 data "
            "rows and the columns username, name, kd, binding_strength, binding, expression, sequence, "
            "dna, pae_interaction, esm_pll, iptm, plddt, similarity_check and design_models. The paper "
            "states 400 designs were tested in round 2, so the row count does not match. design_models "
            "is the entrant's own free-text declaration (for example '[\"Custom PLM\"]'); Section 4.2 "
            "states the organisers 'manually curated and categorized' entrants' workflow summaries into "
            "five design choices, so method identity is self-declared and then curated. Neither the "
            "README's Methods section nor the preprint states how to aggregate these rows into a "
            "per-method or per-category rate, and Section 4.1 reports Figure 8's binder counts 'across "
            "the 3 binding thresholds' without defining them. Under docs/collection.md a value may be "
            "computed from a source's own rows only where the source states the aggregation, so the "
            "per-method rates in Figures 3, 8 and 9 and the 60 affinities in Figure 10 remain "
            "unextracted."
        ),
        locator="results/result_summary.csv header and row count; README.md 'Methods' and 'Data "
                "analysis'; preprint Sections 4.1 and 4.2",
        review_block=rev_repo,
        source_ids=[SOURCE_REPO["id"], SOURCE["id"]],
    ))

    out.append(claim(
        rid("claim", "adaptyv", "hallucination-share-of-binders"),
        "The share of true binders from hallucination designs fell between the Adaptyv rounds",
        "The paper states that hallucinated designs, which became more popular in round 2, supplied a "
        "smaller share of the true binders: 40% in round 1 against 12% in round 2. The denominators "
        "behind these shares are in Figure 9C, which was not read.",
        source=SOURCE, subject=DATASETS["both"]["id"], field="design_category_share_of_binders",
        value=(
            "Section 4.2, verbatim: 'Interestingly, hallucinated designs, despite becoming more "
            "preferred in the second round, had a lower share of true binders (from 40% to 12%, Figure "
            "9 C).' These are shares of the binder set by design category, not hit rates: the number of "
            "designs submitted or tested in each category is printed only in Figure 9, which was not "
            "read. The five curated categories are diversified binders, optimized binders, "
            "physics-based, de novo and hallucination."
        ),
        locator="Section 4.2; Figure 9 caption",
        review_block=rev,
    ))

    return out
