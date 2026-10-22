"""The de novo binder design use case, its relevance judgements, baseline and draft summary.

Nothing here is reviewed. Every judgement and the summary carry status
`needs_review` for a separate review agent.
"""

import adaptyv
import alphaproteo
import bennett
import bindcraft
from common import AREAS, CONTEXTS, DATE, REVIEWED_AT, AGENT_NOTE, claim, link, record, review, rid

USE_CASE_ID = "use-case-de-novo-binder-design"

SOURCE_IDS = [
    alphaproteo.SOURCE["id"],
    bindcraft.SOURCE["id"], bindcraft.SOURCE_SI["id"],
    bennett.SOURCE["id"], bennett.SOURCE_SI["id"],
    adaptyv.SOURCE["id"], adaptyv.SOURCE_REPO["id"],
]

# (protocol record, relevance, endpoint, rationale, constraints, limitations,
#  comparison_group, comparison_title, stratum_label, stratum_order, headline_metric, sources)
JUDGEMENTS = [
    (alphaproteo.PROTOCOLS["yeast-0-2"], "direct",
     "Share of tested AlphaProteo or published-RFdiffusion designs whose yeast-display binding signal "
     "exceeds 0.2, per target, with the number of designs tested",
     "A measured wet-lab binding outcome on seven targets, with the design denominator printed for "
     "every value. It is the only source found where two design methods were measured on the same "
     "assay for the same targets, so it carries the most weight any single source here can. It is not "
     "a controlled comparison: the AlphaProteo authors ran the assay, and Section S4.1 states that the "
     "RFdiffusion arm is the published RFdiffusion designs re-tested rather than RFdiffusion as run by "
     "them.",
     ["Do not read the AlphaProteo and RFdiffusion evaluations on a target as a controlled comparison. "
      "The assay is shared; the design and selection steps are not, and the evaluations' selection, "
      "population and budget comparison fields are null for that reason.",
      "Do not compare these rates with the BLI, SPR or display rates in any other protocol. A binding "
      "signal above 0.2 on this instrument is not the same endpoint as a fitted affinity threshold.",
      "Read each value with its printed denominator. They range from 30 to 172 designs.",
      "Table 1's AlphaProteo values pool up to three different design systems; the Table S2 "
      "evaluations separate them and are the better evidence for what one system achieves."],
     ["Developer-reported: the authors built AlphaProteo, chose the targets, ran the assay and chose "
      "which designs to test with their own filter.",
      "The hit threshold was calibrated manually by visual inspection of raw scatterplots.",
      "No conventional comparator was run on these targets.",
      "No uncertainty is printed for any rate.",
      "Target concentrations were 10- to 20-fold lower than in the RFdiffusion publication, which the "
      "authors say 'may exclude lower-affinity hits'.",
      "Preprint, not peer reviewed."],
     "miniprotein-binder-hit-rates", "Miniprotein binder hit rates by target",
     "AlphaProteo and published RFdiffusion designs, yeast display at signal above 0.2", 1,
     "hit-rate", [alphaproteo.SOURCE["id"]]),

    (alphaproteo.PROTOCOLS["yeast-1-3"], "direct",
     "Share of tested AlphaProteo designs whose yeast-display binding signal exceeds 1.3, on IL-17A",
     "The same measured endpoint as the 0.2-threshold screen but with a different threshold, kept "
     "separate because the threshold is part of the hit definition. It is the clearest single "
     "illustration in the evidence that a hit rate moves with the threshold rather than only with the "
     "method.",
     ["A different hit threshold from the other seven AlphaProteo targets, so this value is not "
      "comparable with them.",
      "Read the value with its printed denominator of 63 designs."],
     ["Developer-reported.",
      "The 1.3 threshold was set to account for background binding on this target and was calibrated "
      "by eye.",
      "One target, one design system, 63 designs. No uncertainty is printed.",
      "No conventional comparator.",
      "Preprint, not peer reviewed."],
     "miniprotein-binder-hit-rates", "Miniprotein binder hit rates by target",
     "AlphaProteo on IL-17A, yeast display at signal above 1.3", 2,
     "hit-rate", [alphaproteo.SOURCE["id"]]),

    (bindcraft.PROTOCOLS["screen"], "direct",
     "Number of tested BindCraft designs with an observed binding signal, per target, with the number "
     "of designs tested",
     "Measured wet-lab binding outcomes on ten of BindCraft's twelve benchmark targets, each with the "
     "design denominator stated in the Results prose. It is the per-target spread the use case needs, "
     "and it is what the headline 46.3% average is built from.",
     ["These are counts, not rates: the paper prints no per-target rate, so no rate is recorded.",
      "The assay is not uniform across targets. Treating the ten targets as one comparison mixes SPR "
      "titration, a BLI screen in a bivalent Fc-fusion format, and an SPR prescreen against soluble "
      "analogues of the target.",
      "Do not compare these counts with the AlphaProteo or Bennett rates; the endpoints differ.",
      "Read each count with its denominator. They range from 6 to 53 designs."],
     ["Developer-reported: the authors built the pipeline, chose the targets and chose which designs to "
      "test.",
      "No numeric binding threshold is stated. A hit is a binding signal that was observed.",
      "The designs tested are about ten of the top twenty ranked by the pipeline's own i_pTM score, so "
      "design and selection are coupled.",
      "Two of the twelve targets, CrSAS-6 and CbAgo, have a stated denominator but no stated "
      "numerator; their numerators are printed only inside the Fig. 1b graphic, which was not read.",
      "No conventional comparator was run.",
      "No uncertainty is printed."],
     "miniprotein-binder-hit-rates", "Miniprotein binder hit rates by target",
     "BindCraft per-target binding screens", 3,
     "count", [bindcraft.SOURCE["id"]]),

    (bindcraft.PROTOCOLS["aggregate"], "direct",
     "Mean and range of BindCraft's per-target experimental success rate over its 12 benchmark targets",
     "The headline claim this use case has to adjudicate, recorded with what it actually is: an "
     "unweighted mean over twelve author-chosen targets whose denominators range from 6 to 53 designs, "
     "spanning rates from 10% to 100%. The range is the finding, not the mean.",
     ["The mean is unweighted over targets, not pooled over designs. A target where 6 of 6 designs "
      "bound contributes as much as one where 13 of 53 did.",
      "Do not compare this mean with any single-target rate in another protocol.",
      "The 10% to 100% range belongs with the mean whenever the mean is cited."],
     ["Developer-reported, with author-chosen targets.",
      "Pools targets measured under different endpoints: SPR, a bivalent-Fc BLI screen, and a soluble "
      "analogue prescreen.",
      "Two of the twelve per-target numerators were not read, so the mean cannot be checked against "
      "the per-target counts in this batch.",
      "No conventional comparator. No uncertainty is printed."],
     "miniprotein-binder-hit-rates", "Miniprotein binder hit rates by target",
     "BindCraft average over 12 targets", 4,
     "hit-rate", [bindcraft.SOURCE["id"]]),

    (bennett.PROTOCOLS["spr96"], "direct",
     "Share of designed antibody variable heavy chains confirmed as binders by single-concentration "
     "SPR after E. coli expression, out of 96 designs screened per target",
     "The antibody end of the spread, and the strongest corrective in the evidence to the miniprotein "
     "hit rates: the same family of methods, on antibody variable domains, gives 0% to 2% where the "
     "miniprotein papers report tens of percent. A measured wet-lab outcome with an exact denominator.",
     ["Do not compare these rates with the miniprotein hit rates as a method ranking. The modality is "
      "different and so is the assay.",
      "Read the IL7R 0% as a measured zero over 96 designs, not as a missing value.",
      "The main text states 95 designs per target while Table 6 prints 96; the table value is "
      "recorded."],
     ["Developer-reported: the authors fine-tuned RFdiffusion, chose the targets, chose the filter and "
      "ran the screens.",
      "The designs tested passed the authors' own fine-tuned RoseTTAFold2 filter at a setting the "
      "table caption calls 'likely not the most predictive', so design and selection are coupled and "
      "the paper itself attributes the low rates partly to the filter.",
      "No numeric SPR response or affinity threshold is printed for what counts as a confirmed binder.",
      "No conventional comparator (immunisation, hybridoma or library selection) was run on these "
      "targets.",
      "No uncertainty is printed.",
      "Two design targets, RSV-F site I and HIV Env, have no printed outcome at all."],
     "antibody-binder-hit-rates", "Antibody variable-domain hit rates by target",
     "Fine-tuned RFdiffusion VHHs, 96 designs per target by SPR", 1,
     "hit-rate", [bennett.SOURCE_SI["id"], bennett.SOURCE["id"]]),

    (bennett.PROTOCOLS["ysd9000"], "direct",
     "Share of designed antibody variable heavy chains confirmed as binders after yeast surface display "
     "screening of 9,000 designs per target with SPR confirmation",
     "The largest denominators in the whole evidence set, and the clearest demonstration that effort "
     "and hit rate are not the same claim: 9,000 designs per target yield 0.01% to 0.2%. The influenza "
     "H1 stem target was screened both ways, so this protocol and the 96-design SPR protocol can be "
     "read side by side on one target.",
     ["Do not compare these rates with the 96-design SPR rates as if they were the same experiment. On "
      "H1 stem the same design campaign gives 1% over 96 designs by SPR and 0.2% over 9,000 by display.",
      "Do not compare with the miniprotein hit rates as a method ranking.",
      "Read each rate with its 9,000-design denominator."],
     ["Developer-reported.",
      "The designs screened passed the authors' own filter at a setting the table caption calls "
      "'likely not the most predictive'.",
      "No numeric display-signal or affinity threshold is printed for what counts as a confirmed "
      "binder.",
      "No conventional comparator was run, although the discussion contrasts the approach with yeast "
      "display selection from random libraries.",
      "No uncertainty is printed."],
     "antibody-binder-hit-rates", "Antibody variable-domain hit rates by target",
     "Fine-tuned RFdiffusion VHHs, 9,000 designs per target by yeast display", 2,
     "hit-rate", [bennett.SOURCE_SI["id"], bennett.SOURCE["id"]]),

    (adaptyv.PROTOCOLS["binding"], "direct",
     "Share of selected competition designs confirmed as binders to EGFR by a third-party automated "
     "cell-free expression and BLI pipeline",
     "The only source found where designs from many methods were tested on one target, by one "
     "laboratory, on one assay, with the measurement independent of the design methods. That "
     "independence is worth more than anything else in the evidence set. What it cannot deliver is a "
     "per-method rate: the methods are the entrants' own declarations, the organisers hand-picked most "
     "of the tested set for diversity, and the three binding thresholds behind the figure counts are "
     "never defined.",
     ["Do not read the round-to-round change as a method effect. The design population, the ranking "
      "metric and the number of participants all changed between rounds.",
      "Do not attribute the round-level rates to any design method. Per-method rates are not "
      "extractable from this source.",
      "The round 1 rate is printed twice with different values, 2.5% in Section 2.4 and 3% in Section "
      "4.2; both are recorded and neither is preferred.",
      "The hit definition is null with a reason. Do not substitute a threshold from another protocol."],
     ["No hit definition is printed anywhere in the paper.",
      "The tested set is not a sample of any method's output: 101 of 201 round-1 and 300 of 400 "
      "round-2 designs were hand-picked by the organisers for diversity.",
      "Entrants chose how many designs to submit and how much effort to spend, so effort is "
      "uncontrolled.",
      "Design methods are self-declared by entrants and then curated by the organisers into five "
      "categories.",
      "Written by the organisers, who ran the assay.",
      "No conventional comparator arm. EGF and cetuximab were positive controls.",
      "Preprint, not peer reviewed. No uncertainty is printed."],
     "same-target-cross-method", "One target, one assay, many methods (EGFR)",
     "Adaptyv EGFR competition rounds 1 and 2", 1,
     "hit-rate", [adaptyv.SOURCE["id"], adaptyv.SOURCE_REPO["id"]]),

    (alphaproteo.PROTOCOLS["htrf-kd"], "direct",
     "Lowest dissociation constant measured by HTRF among a target's expressed AlphaProteo or "
     "published-RFdiffusion yeast-display hits",
     "The affinities reached are part of the endpoint this use case needs, and these are measured "
     "values with a stated assay. They answer 'how good is the best design' and not 'how many designs "
     "bind'.",
     ["A best-of-subset value. It describes the best design found among the hits that expressed, not "
      "the distribution of the designs.",
      "Do not compare HTRF values with BLI or SPR values. Section S4.2 reports that HTRF gave KD "
      "values about tenfold higher than published BLI values for two control binders.",
      "The AlphaProteo and RFdiffusion affinity evaluations are not a controlled comparison, for the "
      "same reason as the hit rates."],
     ["Developer-reported.",
      "Best-of-subset over a set the authors chose to follow up; no uncertainty is printed.",
      "The subset titrated is the yeast hits that expressed in E. coli, so the affinity carries the "
      "expression filter as well as the design and binding filters.",
      "Preprint, not peer reviewed."],
     "binder-affinities", "Affinity of the best binder found per target",
     "AlphaProteo and published RFdiffusion designs, HTRF", 1,
     "dissociation-constant", [alphaproteo.SOURCE["id"]]),

    (bindcraft.PROTOCOLS["affinity"], "direct",
     "Dissociation constant of the highest-affinity BindCraft binder per target, without experimental "
     "sequence optimisation",
     "Measured affinities on eleven targets, spanning three orders of magnitude from about 5 nM to 5.7 "
     "micromolar. Useful for the 'how good is the best design' half of the endpoint and for showing "
     "that a high hit rate does not imply a high affinity.",
     ["A best-of-subset value per target.",
      "Several values are apparent constants rather than fitted monovalent constants, including a "
      "bivalent Fc-fusion measurement whose avidity inflates apparent affinity, and two values the "
      "source states only in words.",
      "Mixed assays: SPR for most targets, BLI for PD-1 and CbAgo.",
      "Do not compare with the AlphaProteo HTRF values."],
     ["Developer-reported.",
      "Best-of-subset; no uncertainty is printed.",
      "Mixed assays and mixed construct formats.",
      "Two of the eleven values are not numeric in the source ('lower than 1 nM', 'in the range of 300 "
      "nM') and are recorded with a null numeric value."],
     "binder-affinities", "Affinity of the best binder found per target",
     "BindCraft, SPR and BLI", 2,
     "dissociation-constant", [bindcraft.SOURCE["id"]]),

    (adaptyv.PROTOCOLS["affinity"], "direct",
     "Dissociation constant for EGFR of a competition design, fitted from third-party multi-cycle "
     "kinetic BLI",
     "Affinities measured by an independent laboratory on one target, including the only same-assay "
     "measurement of a conventionally obtained binder anywhere in this evidence: cetuximab at 9.94 nM "
     "on the same instrument as the designs. The best de novo design reached 82 nM and the best "
     "optimised antibody 1.21 nM.",
     ["The 1.21 nM winner is an optimisation of cetuximab, not a de novo design, so it is not "
      "comparable with de novo affinities.",
      "Cetuximab's 9.94 nM is a positive control for assay validity. It says what a conventional "
      "binder achieves on this target; it says nothing about the hit rate of conventional methods, "
      "because no library campaign was run.",
      "Only the affinities printed in the prose are recorded. The distribution over all 60 binders is "
      "in Figure 10, which was not read."],
     ["Preprint, not peer reviewed, written by the organisers.",
      "Only a handful of the 60 measured affinities are printed in the prose.",
      "Section 4.3 reports no statistically significant difference in median affinity between the two "
      "rounds.",
      "No uncertainty is printed in the prose for individual values."],
     "binder-affinities", "Affinity of the best binder found per target",
     "Adaptyv EGFR competition, third-party BLI", 3,
     "dissociation-constant", [adaptyv.SOURCE["id"], adaptyv.SOURCE_REPO["id"]]),

    (alphaproteo.PROTOCOLS["ecoli-funnel"], "proxy",
     "Counts of AlphaProteo yeast-display hits that were selected for E. coli expression, subcloned and "
     "expressed, tested by HTRF, and showed HTRF binding, per target",
     "Proxy evidence. The issue asks for the filtering funnel to be recorded, and this is the only "
     "source that prints it stage by stage. It measures attrition between a display hit and a "
     "confirmed, expressible binder, which is not the binding endpoint itself but is what determines "
     "how much work a hit rate actually buys.",
     ["These are counts of designs surviving a stage, not a hit rate. The first stage's denominator is "
      "an author choice and is not printed.",
      "Do not use these counts to recompute the hit rates: the number of yeast hits available to "
      "select from is not stated."],
     ["Developer-reported.",
      "The number of yeast hits selected for follow-up is an author choice, not the full hit set, so "
      "the funnel cannot be closed back to the screen.",
      "TNF-alpha has no column, consistent with its 0% hit rate; its absence is not a recorded zero.",
      "Preprint, not peer reviewed."],
     "pipeline-attrition", "Attrition between a screen hit and a confirmed binder",
     "AlphaProteo yeast hits through E. coli expression and HTRF", 1,
     "count", [alphaproteo.SOURCE["id"]]),

    (adaptyv.PROTOCOLS["expression"], "proxy",
     "Share of selected competition designs that expressed above 0.02 micrograms per millilitre in a "
     "third-party cell-free system",
     "Proxy evidence. Expression is a precondition for a binding measurement, not the binding endpoint, "
     "but it is measured independently of the design methods and it is the stage where the competition "
     "improved most between rounds, from 73% to 94 or 95%.",
     ["Expression is not binding. Do not read an expression rate as evidence that a workflow produces "
      "working binders.",
      "The round 2 rate is printed twice, as 95% (378 of 400) in Section 2.4 and as 94% in Section "
      "4.1; both are recorded."],
     ["Preprint, not peer reviewed, written by the organisers.",
      "The improvement is confounded with the change of ranking metric, the change of design "
      "population and the change of participants between rounds.",
      "No uncertainty is printed."],
     "pipeline-attrition", "Attrition between a screen hit and a confirmed binder",
     "Adaptyv EGFR competition, third-party cell-free expression", 2,
     "proportion", [adaptyv.SOURCE["id"]]),

    (bennett.PROTOCOLS["rf2"], "outside_scope",
     "Share of designed antibody variable heavy chains that pass a fine-tuned RoseTTAFold2 filter, at "
     "three proportions of interface hotspots provided",
     "Outside the use case's endpoint. This is a computational filter pass rate, which the issue "
     "defines as a step inside the pipeline rather than an outcome. It is kept because it quantifies "
     "the filter that chose the tested designs, and because the table caption gives its purpose as "
     "estimating compute requirements, not as evidence about binders.",
     ["Not an outcome. Do not present these values alongside measured hit rates.",
      "Use them only to describe how the tested set was chosen and how much compute a design library "
      "costs."],
     ["An in silico filter pass rate, not a measured outcome.",
      "The filter is the authors' own, and the caption states that the setting used for filtering in "
      "the work 'is likely not the most predictive setting'.",
      "The H1 stem 9,000-design row repeats the 96-design row's values in parentheses, because both "
      "come from one design campaign.",
      "No uncertainty is printed."],
     "in-silico-filters", "Computational filters used to choose which designs to test",
     "Fine-tuned RoseTTAFold2 filter pass rates", 1,
     "success-rate", [bennett.SOURCE_SI["id"]]),

    (bennett.PROTOCOLS["af3"], "outside_scope",
     "Share of designed antibody variable heavy chains that pass an AlphaFold3 filter at Ca RMSD below "
     "5 A and ipTM above 0.5",
     "Outside the use case's endpoint, and retrospective: AlphaFold3 was released after the design "
     "work. Kept because the paper uses it to argue that a better filter would raise the measured "
     "success rate, which is a claim about the selection step that the use case has to keep separate "
     "from the design step.",
     ["Not an outcome, and retrospective.",
      "The values are depressed by AlphaFold3 re-predicting the cropped design targets inaccurately, "
      "which the caption states explicitly.",
      "Do not read a low AlphaFold3 pass rate as evidence about the designs."],
     ["An in silico filter pass rate, not a measured outcome.",
      "Retrospective: the filter was not available when the designs were made.",
      "The caption states that cropped targets were not accurately re-predicted and that 'success "
      "rates would likely be higher with contiguous (non-cropped) targets'.",
      "The RSV site 3 value carries an asterisk recording a 19 A target-epitope prediction error.",
      "No uncertainty is printed."],
     "in-silico-filters", "Computational filters used to choose which designs to test",
     "AlphaFold3 filter pass rates", 2,
     "success-rate", [bennett.SOURCE_SI["id"]]),
]

EXCLUSIONS = [
    "Hit definitions are not commensurable across these sources. A yeast-display flow-cytometry signal "
    "above 0.2, a BLI KD below 1000 nM, an SPR response at half the positive control, and 'nanomolar "
    "with a human serum albumin counter-screen' are four different endpoints, and the hit rate moves by "
    "tens of percentage points depending on which is used.",
    "Denominators are small and author-selected, and the designs tested are the top-ranked ones by each "
    "method's own filter, so the design step and the selection step are coupled. Changing only the "
    "filter moved AlphaProteo's PD-L1 rate from 9.6% over 94 designs to 16.1% over 31.",
    "The spread within a single method across targets is wider than any plausible difference between "
    "methods: AlphaProteo 0% to 88%, BindCraft 10% to 100%, Bennett 0% to 2% for antibodies. A method "
    "ranking built from these numbers would mostly be measuring which targets each group chose.",
    "No source includes a conventional comparator (directed evolution, library display selection or "
    "grafting from a known complex) on the same targets as a design method. Cetuximab's 9.94 nM in the "
    "Adaptyv assay is a positive control for assay validity, not a comparator arm: no candidate set was "
    "tested and there is no denominator behind it.",
    "The evidence here does not support a workflow recommendation. It supports per-method, per-target "
    "statements about what happened when designs were made and tested.",
    "An in silico score (interface predicted aligned error, ipTM, predicted local distance difference "
    "test, self-consistency RMSD) is a filter inside the pipeline, not an outcome. Filter pass rates "
    "are recorded as outside the use case's endpoint.",
    "Almost all of the measured evidence is author-reported by the group that built the method. Only "
    "the Adaptyv competition measurements are independent of the design methods, and they are on one "
    "target with no hit definition printed.",
    "Research only. None of this evidence establishes therapeutic efficacy, developability or clinical "
    "suitability for any designed binder.",
]

EVIDENCE_GAPS = [
    "No conventional comparator exists in the retrieved evidence. Not one of the sources runs directed "
    "evolution, library display selection or grafting from a known complex on the same targets as a "
    "design method, with the same expression and assay pipeline and the same hit definition. This is "
    "the primary gap and it cannot be closed by extracting more of these papers; it needs a pass over "
    "the display and directed-evolution literature, or a measurement.",
    "No source anywhere runs two design methods and a conventional comparator on the same targets with "
    "one assay and one hit definition, so the use case's own question cannot currently be answered.",
    "BenchBB (benchbb.bio) was not retrieved. Its seven-target list, protocol, assay and whether any "
    "method has been run on it are unknown, and no results on BenchBB were found for any method.",
    "ProtDBench (arXiv:2605.04118 v2) was not retrieved; only its abstract was read in the search pass. "
    "It is the only candidate standing benchmark for binder design found, and nothing is claimed about "
    "it here.",
    "The single-target binder design literature was not retrieved. The search pass surfaced a large "
    "population of one-off papers, each reporting a hit rate for one target with its own assay "
    "(Francisella virulence factor, deltacoronavirus, Nipah, Langya and measles receptor-binding "
    "domains, GDF15-GFRAL, RH5, canine and human TNF-alpha, HSP90, CCL25, BRD3). Taken together they "
    "are the largest untapped pool of measured outcomes and the place where publication bias will be "
    "worst.",
    "Adaptyv per-method and per-category hit rates were not extracted. The round 2 repository publishes "
    "one row per design with a binding flag and an affinity, but neither the repository nor the paper "
    "states an aggregation over those rows, the method labels are entrants' free text, and the three "
    "binding thresholds behind the Figure 8 counts are never defined.",
    "The Adaptyv round 1 repository, raw kinetic curve package, neutralisation package and structure "
    "predictions were not retrieved, and the 60 measured affinities in Figure 10 were not read.",
    "BindCraft's per-target numerators for CrSAS-6 and CbAgo were not obtained. They are printed only "
    "inside the Figure 1b graphic, which was not read, and Supplementary Data 1 does not let them be "
    "recomputed: the row filter that reconciles with the prose for nine targets fails for PD-L1, "
    "CrSAS-6 and CbAgo.",
    "BoltzGen (bioRxiv 10.1101/2025.11.20.689494) Tables 2 and 3 were not extracted. It reports a "
    "cold-start against warm-start split (6 of 9 novel targets against 4 of 5 benchmark targets with "
    "known binders) that is exactly the protocol limit the use case needs, and some of its data are "
    "stated to be temporarily confidential.",
    "Filius et al. 2025 (ACS Chem Biol 10.1021/acschembio.5c00774) Supporting Information Table S3 was "
    "not extracted. It is a third-party wet-lab test of BindCraft on four targets that reports the two "
    "targets which failed outright, which is the kind of independent evidence this use case is "
    "shortest of.",
    "The Nature Communications minibinder paper (doi 10.1038/s41467-026-76760-5) was not extracted. It "
    "is the closest thing found to an independent replication: one group, one assay, three targets of "
    "differing difficulty with the same method.",
    "PXDesign's own measured values (bioRxiv 10.1101/2025.08.15.670450, Tables 1 and 2) were not "
    "extracted. Its baseline column is deliberately excluded: those numbers are copied from "
    "publications and partly adjusted by the PXDesign authors using their own HTRF data, which is a "
    "third party's reanalysis.",
    "The values in AlphaProteo's 'Other design methods' rows and its 'RFdiffusion (published)' row are "
    "recorded only as a transcription claim, not as results, for the same reason: they are copied from "
    "publications this pass did not retrieve, and Section S4.2 states that the asterisked values were "
    "re-measured by the AlphaProteo authors and that for PD-L1 they substituted a different design for "
    "the published best one. The primary sources behind those cells (Procko et al., Gainza et al., Cao "
    "et al., Berger et al., Yang et al., Watson et al.) were not retrieved.",
    "Junker and Schoeder 2026 (PLOS ONE 10.1371/journal.pone.0355549) is the most careful cross-method "
    "comparison found and has no wet-lab arm, so it supplies no outcome. Nanda 2026 "
    "(doi 10.21203/rs.3.rs-11106209/v1) on amyloid fibrils is likewise in silico only. Amyloid fibrils "
    "and GPCR peptide targets are target classes for which no measured binder design outcome was found "
    "at all.",
    "No source reports uncertainty for any hit rate or affinity. Every rate in this use case is a point "
    "value over a denominator between 6 and 9,000, with no interval.",
    "No source connects a designed binder to a downstream outcome such as efficacy, developability or "
    "manufacturability.",
    "Automated source review only. Independent human scientific review remains outstanding, and nothing "
    "here has been experimentally replicated.",
]

SEARCH_TERMS = [
    "de novo binder design", "protein binder design", "miniprotein", "nanobody design",
    "antibody design", "experimental success rate", "hit rate", "binding affinity",
    "yeast surface display", "biolayer interferometry", "surface plasmon resonance",
    "RFdiffusion", "BindCraft", "AlphaProteo", "BoltzGen", "ProteinMPNN",
    "directed evolution", "display selection", "epitope grafting",
]

USE_CASE = record(
    USE_CASE_ID, "use_case",
    "Design a new binder to a chosen target",
    "Which computational design workflow produces binders that work when they are made and tested?",
    facets={"areas": ["proteins-complexes", "protein-structure"], "contexts": CONTEXTS},
    source_ids=SOURCE_IDS,
    links=[link("assessed_by", p["id"]) for p, *_ in JUDGEMENTS],
    attributes={
        "slug": "de-novo-binder-design",
        "question": "Which computational design workflow produces binders that work when they are made "
                    "and tested?",
        "intended_users": [
            "Protein engineers choosing a design workflow for a new target",
            "Structural and molecular biologists who need a reagent-grade binder to a specific epitope",
            "Groups deciding how many designs to synthesise and assay for a given budget",
        ],
        "decision": "Choose a computational design workflow for a new target, and decide how many "
                    "designs to synthesise and assay.",
        "inputs": [
            "A target structure or a structure prediction, and the epitope or hotspot residues to "
            "target",
            "Whether the target has a known binder or a solved complex, which decides whether this is "
            "a cold start",
            "The binder modality required: miniprotein, antibody variable domain, nanobody or peptide",
            "A synthesis and assay budget, and the assay that will define a hit",
            "Expression, solubility and format constraints on the designs that can be tested",
        ],
        "output": "A design workflow choice and a testing plan, with the share of designs expected to "
                  "bind at a stated assay threshold, the affinities reached, and the number of designs "
                  "that must be made to get there.",
        "setting": "Research protein engineering for one target at a time. Miniprotein, antibody "
                   "variable-domain and peptide binders require separate comparisons; a rate measured "
                   "on one modality does not transfer to another.",
        "exclusions": EXCLUSIONS,
        "clinical_scope": "Research only. A measured binding outcome does not establish efficacy, "
                          "developability, immunogenicity or clinical suitability, and nothing here "
                          "supports any therapeutic use of a designed binder.",
        "evidence_gaps": EVIDENCE_GAPS,
        "search_terms": SEARCH_TERMS,
        "citation_locators": [
            {"source_id": alphaproteo.SOURCE["id"],
             "locator": "Table 1; Table S2; Table S3; Sections S1.2.1, S2, S4.1 and S4.2"},
            {"source_id": bindcraft.SOURCE["id"],
             "locator": "Introduction, final paragraph; Fig. 1b caption; Results sections 'Binders "
                        "targeting cell-surface receptors', 'Targeting unexplored binding sites', "
                        "'Masking allergenic epitopes' and 'Modulating multi-domain nucleases'"},
            {"source_id": bindcraft.SOURCE_SI["id"],
             "locator": "Supplementary Table 1; Supplementary Data 1"},
            {"source_id": bennett.SOURCE["id"],
             "locator": "Results paragraph 2; 'Improved oracles increase success rate'"},
            {"source_id": bennett.SOURCE_SI["id"],
             "locator": "Supplementary Methods Tables 5 and 6; Section 6.8"},
            {"source_id": adaptyv.SOURCE["id"],
             "locator": "Abstract; Sections 2.1 to 2.4, 3.1, 3.2, 4.1, 4.2 and 4.3"},
            {"source_id": adaptyv.SOURCE_REPO["id"],
             "locator": "results/result_summary.csv and README.md Methods at commit "
                        "fc91b91ddc367830b755b215dbc69669675ad6a0"},
        ],
        "collection_plan": {
            "status": "planned",
            "comparison_question": "On the same targets, with one expression and assay pipeline and one "
                                   "hit definition, how does the share of designs that bind differ "
                                   "between two design workflows and a conventional comparator at the "
                                   "same testing budget?",
            "baselines": [
                "Directed evolution or library display selection from a naive library on the same "
                "target",
                "Grafting from a solved complex with a known binder, where one exists",
            ],
            "outcomes": [
                "Share of designs that bind at a single stated threshold on one assay, with the "
                "denominator",
                "Affinity distribution of the binders found, not only the best one",
                "The full funnel: designs generated, ordered, expressed, assayed and confirmed",
                "Designs that had to be made per binder obtained, at a fixed budget",
            ],
            "validation_requirements": [
                "Fix the hit definition before the comparison and apply it to every arm.",
                "Separate the design step from the selection step: report the rate over a random sample "
                "of generated designs as well as over the filter's top picks.",
                "Match the targets across arms and state for each whether it has a known binder or a "
                "solved complex.",
                "Report the denominator and an interval for every rate.",
                "Keep modalities apart: miniprotein, antibody variable domain and peptide results are "
                "not interchangeable.",
            ],
            "next_step": "Retrieve BenchBB and ProtDBench to establish whether a standing binder design "
                         "benchmark with a fixed hit definition exists, and run a separate literature "
                         "pass for conventional display and directed-evolution arms on any target that "
                         "a design paper also reports.",
        },
        "evidence_checked": {
            "date": DATE,
            "cutoff_date": DATE,
            "records": [
                "data/omics/lit-search-20261022-uc-binder/report.md",
                "data/omics/use-case-coverage-binder-20261022/research.md",
                "data/omics/search-ledger.jsonl",
            ],
        },
    },
)

SUMMARY_VALUE = (
    "Nine sources carry measured outcomes for de novo binder design and none of them answers which "
    "workflow to use, because no paper runs two design methods and a conventional comparator on the "
    "same targets with one assay and one hit definition.\n\n"
    "What the measured evidence shows is that the target matters more than the method. AlphaProteo's "
    "yeast-display success rate across eight targets runs from 0% over 54 designs on TNF-alpha to 88% "
    "over 94 designs on BHRF1, at a binding-signal threshold of 0.2 (1.3 on IL-17A). BindCraft reports "
    "an average experimental success rate of 46.3% over twelve targets with a range of 10% to 100%, "
    "built from per-target counts as small as 2 binders from 7 designs on Bet v1 and as large as 6 from "
    "6 on the SpCas9 REC1 domain. The same family of methods applied to antibody variable domains is "
    "two orders of magnitude worse: fine-tuned RFdiffusion gives 2% over 96 designs on TcdB, 0% over 96 "
    "on IL-7 receptor alpha, and 0.01% to 0.2% over 9,000 designs per target by yeast display. On "
    "influenza H1 stem the same design campaign gives 1% over 96 designs by SPR and 0.2% over 9,000 by "
    "display, so the screening method moves the rate as much as the target does.\n\n"
    "Nearly all of this is author-reported by the group that built the method, which also chose the "
    "targets, ran the assay and chose which designs to test. The exception is the Adaptyv EGFR "
    "competition, where a third-party laboratory expressed and measured designs from many entrants on "
    "one target and one assay: 2.5% of 201 round-1 designs bound (printed elsewhere in the same paper "
    "as 3%), and 53 of 400 round-2 designs bound, printed as 13%. That source cannot be turned into a "
    "per-method rate: design methods are the entrants' own declarations, the organisers hand-picked 101 "
    "of 201 round-1 and 300 of 400 round-2 designs for diversity, and the three binding thresholds "
    "behind the figure counts are never defined.\n\n"
    "Affinities reached are better than the hit rates suggest. AlphaProteo's best measured binder was "
    "0.082 nM on IL-7 receptor alpha by HTRF; BindCraft's best ranged from 5 nM on CbAgo to 5.7 "
    "micromolar "
    "on CrSAS-6; the best de novo design in the Adaptyv competition reached 82 nM and the winning "
    "optimised cetuximab fragment 1.21 nM, against 9.94 nM for the cetuximab positive control measured "
    "on the same instrument.\n\n"
    "Three things stop these numbers from ranking methods. The hit definitions are different "
    "endpoints, not different thresholds on one endpoint. The denominators are small and chosen, and "
    "the designs tested are the top picks of each method's own filter, so design and selection are "
    "coupled: changing only AlphaProteo's filter moved its PD-L1 rate from 9.6% over 94 designs to "
    "16.1% over 31, and the Bennett authors attribute their low antibody rates partly to a filter they "
    "describe as weak. And the spread within one method across targets is wider than any plausible "
    "difference between methods. No conventional comparator is run anywhere in this evidence, so there "
    "is no measurement of what a designed binder is being compared against."
)


def build():
    out = [USE_CASE]
    for (proto, relevance, endpoint, rationale, constraints, limitations,
         group, group_title, stratum, order, headline, sources) in JUDGEMENTS:
        short = proto["id"].replace("uc-binder-20261022-protocol-", "")
        out.append(record(
            f"use-case-mapping-binder-20261022-{short}",
            "claim",
            f"Relevance of {proto['id']} to \"Which computational design workflow produces binders "
            f"that work when they are made and tested?\"",
            rationale,
            status="needs_review",
            source_ids=sources,
            links=[link("subject", USE_CASE_ID)],
            attributes={
                "field": f"links:assessed_by:{proto['id']}",
                "value": proto["id"],
                "relevance": relevance,
                "endpoint": endpoint,
                "rationale": rationale,
                "constraints": constraints,
                "limitations": limitations,
                "citation_locators": [
                    {"source_id": sid, "locator": proto["attributes"]["source_locator"]}
                    for sid in sources
                ],
                "source_locator": "; ".join(
                    f"{sid}: {proto['attributes']['source_locator']}" for sid in sources),
                "comparison_group": group,
                "comparison_title": group_title,
                "stratum_label": stratum,
                "stratum_order": order,
                "headline_metric": headline,
                "revision": 1,
                "reason": "Add measured de novo binder design outcomes from the 2026-10-22 use-case "
                          "evidence pass (#176).",
                "review": {
                    "method": ["scope-review"],
                    "reviewer": ["claude"],
                    "reviewer_note": AGENT_NOTE,
                    "date": DATE,
                    "reviewed_at": REVIEWED_AT,
                    "note": "Judgement recorded by the agent that extracted the evidence, with status "
                            "needs_review. A different worker must review the endpoint fit, the "
                            "relevance grade, the constraints and the grouping, and list the "
                            "evaluations it checked, before this judgement counts as evidence. No "
                            "execution, reproduction, human scientific review or clinical validation.",
                },
            },
        ))

    out.append(claim(
        "use-case-baseline-binder-20261022",
        "Baseline for the de novo binder design use case",
        "Directed evolution, library display selection and grafting from a known complex are the "
        "established routes to a new binder that a design workflow has to beat. No source retrieved in "
        "this pass runs any of them as an arm on the same targets as a design method, so the baseline "
        "is named and recorded as unmeasured.",
        source=adaptyv.SOURCE, subject=USE_CASE_ID, field="baseline",
        value="Directed evolution, display selection or grafting",
        locator="Adaptyv preprint Sections 2.3 and 3.2 (EGF and cetuximab as positive controls; "
                "cetuximab at 9.94 nM); Bennett 2025 Discussion (contrast with yeast display selection "
                "from random libraries); AlphaProteo Table 1 caption ('Binders derived from "
                "selection-based methods, such as antibodies and nanobodies, are not considered here')",
        review_block=review(adaptyv.SOURCE, ["scope-review"],
                            "Named from the issue's requirement and the sources' own statements about "
                            "what they did not run.",
                            "Baseline claim recorded by the extracting agent with status needs_review."),
        source_ids=[adaptyv.SOURCE["id"], bennett.SOURCE["id"], alphaproteo.SOURCE["id"]],
        extra={
            "method_ids": [adaptyv.METHOD_CONVENTIONAL["id"]],
            "rationale": (
                "Before machine-learning design, a new binder to a chosen target came from iterated "
                "selection: directed evolution, phage or yeast display from a naive or immunised "
                "library, or grafting a known binding motif from a solved complex. Those are what a "
                "design workflow replaces, so they are the reference. The evidence this pass retrieved "
                "contains no such arm on any target a design method was also run on. Its only "
                "same-assay trace is cetuximab, an approved antibody obtained by conventional "
                "discovery, measured at 9.94 nM as a positive control in the Adaptyv EGFR assay, and "
                "AlphaProteo's Table 1 caption states that 'binders derived from selection-based "
                "methods, such as antibodies and nanobodies, are not considered here'. The baseline is "
                "therefore recorded as named but unmeasured, and the absence of a comparator is the "
                "use case's primary evidence gap."
            ),
            "revision": 1,
            "reason": "Name the use case's pre-machine-learning comparator for the 2026-10-22 evidence "
                      "pass (#176).",
        },
    ))

    out.append(claim(
        "use-case-summary-binder-20261022",
        "Summary of the de novo binder design evidence",
        "A descriptive account of what the reviewed evidence shows about de novo binder design: the "
        "per-target spread, the antibody-versus-miniprotein gap, the author-reported nature of nearly "
        "all of it, and the absence of any controlled cross-method comparison. It makes no "
        "recommendation.",
        source=alphaproteo.SOURCE, subject=USE_CASE_ID, field="summary",
        value=SUMMARY_VALUE,
        locator="AlphaProteo Table 1, Table S2 and Sections S1.2.1, S2 and S4.1; BindCraft Introduction "
                "and Results prose; Bennett Supplementary Methods Table 6; Adaptyv Sections 2.3, 2.4, "
                "3.1, 3.2, 4.1, 4.2 and 4.3",
        review_block=review(alphaproteo.SOURCE, ["scope-review"],
                            "Drafted from the results in this batch; every number in the summary is "
                            "traceable to a result record or a claim in the same batch.",
                            "Draft summary recorded by the extracting agent with status needs_review. A "
                            "different worker must check every number against its result record and "
                            "confirm that the summary makes no recommendation, before it is published."),
        source_ids=SOURCE_IDS,
        extra={
            "revision": 1,
            "reason": "Draft the use case's summary for the 2026-10-22 evidence pass (#176).",
        },
    ))

    return out
