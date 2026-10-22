"""BindCraft (Nature, doi 10.1038/s41586-025-09429-6) per-target outcomes.

The per-target numerators and denominators are printed in the Results prose;
Figure 1b repeats them inside graphic boxes, which this pass did not read. Two
targets (CrSAS-6 and CbAgo) have a denominator in the prose but no numerator,
so no hit count is recorded for them.

Supplementary Data 1 carries one row per tested design with a Binding column.
Counting it would reproduce the figure's stated aggregation, but the row filter
is ambiguous: dropping rows with an empty Binding cell reconciles with the prose
for nine of twelve targets and not for PD-L1, CrSAS-6 or CbAgo. Under
docs/collection.md ("a filter the rows do not let you apply") that is a gap, not
a computation.
"""

from common import (AREAS, claim, comparison, evaluation, facets, link, missing, record,
                    result, review, rid)

SOURCE = record(
    rid("source", "bindcraft"), "source",
    "One-shot design of functional protein binders with BindCraft (Pacesa et al., Nature 2025)",
    "Primary source retrieved and hashed for the 2026-10-22 de novo binder design extraction "
    "(issue #176).",
    facets=facets(),
    attributes={
        "url": "https://doi.org/10.1038/s41586-025-09429-6",
        "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12507698/fullTextXML",
        "version": "Nature, version of record; Europe PMC JATS full text for PMC12507698",
        "retrieved_at": "2026-10-22T11:55:00Z",
        "artifact_sha256": "74bd2902d46460ec387ed6ee46b5bf8fe61b9ea09f2d7be4daa2046ac7e59d5d",
        "doi": "10.1038/s41586-025-09429-6",
        "publication_status": "peer_reviewed",
        "licence": "CC-BY-NC-ND-4.0",
        "media_type": "application/xml",
        "source_locator": "Results sections 'Accurate design of de novo binders' through 'AAV "
                          "retargeting for gene delivery'; Fig. 1b caption",
        "retrieval_method": "Europe PMC REST fullTextXML endpoint, flattened to text for reading. The "
                            "PMC article PDF was refused (HTTP 404 through the instance path).",
        "limitations": [
            "Developer-reported: the BindCraft authors built the pipeline, chose the targets and chose "
            "which designs to test.",
            "Fig. 1b prints the per-target numerator and denominator inside graphic boxes. Those boxes "
            "are not in the JATS text and were not read from the figure image. Where the Results prose "
            "states the counts they are recorded from the prose; where it does not (CrSAS-6, CbAgo) no "
            "hit count is recorded.",
            "The assay is not uniform across targets. Fig. 1b's caption defines a successful design as "
            "one 'where binding was observed on SPR measurement', but PD-1 was screened by BLI in a "
            "bivalent Fc-fusion format and the claudin binders were prescreened against soluble "
            "analogues rather than the wild-type target.",
            "Denominators are 6 to 53 designs per target and the tested designs are the top-ranked ones "
            "by the authors' own in silico filter, so design and selection are coupled.",
            "No conventional comparator was run. The RFdiffusion comparison in Extended Data Fig. 1c is "
            "generation time and in silico success rate, and Extended Data Fig. 7 is reprediction of "
            "published designs.",
            "No uncertainty is printed for any per-target rate or count.",
        ],
        "evidence_concerns": [
            {
                "source_id": rid("source", "bindcraft"),
                "message": (
                    "Supplementary Data 1 has one row per tested design with a Binding column holding 1, "
                    "0 or an empty cell. Treating the non-empty cells as the tested set reproduces the "
                    "prose counts for BBF-14 (11 tested, 6 binding), Bet v1 (7, 2), CD45 (16, 4), Der f7 "
                    "(10, 4), Der f21 (7, 4), IFNAR2 (9, 3), PD-1 (53, 13), SpCas9 (6, 6) and CLDN1 "
                    "(7, 6), but not for PD-L1 (13 non-empty rows with 11 binding against 9 tested with "
                    "7 binding in the prose), CrSAS-6 (10 non-empty rows against 9 tested) or CbAgo (2 "
                    "non-empty rows against 12 tested). The row filter is therefore ambiguous and no "
                    "value is computed from these rows."
                ),
                "source_locator": "Supplementary Data 1 (41586_2025_9429_MOESM4_ESM.csv), columns "
                                  "Target, DesignName, Binding; Results prose; Fig. 1b caption",
                "artifact_sha256": "74bd2902d46460ec387ed6ee46b5bf8fe61b9ea09f2d7be4daa2046ac7e59d5d",
                "review_date": "2026-10-22",
            },
            {
                "source_id": rid("source", "bindcraft"),
                "message": (
                    "Fig. 1b's caption defines success as binding observed on SPR, but the PD-1 screen "
                    "was BLI in a bivalent Fc-fusion format and the CLDN1 screen used soluble analogues. "
                    "The 46.3% average therefore pools targets measured under different endpoints."
                ),
                "source_locator": "Fig. 1b caption; Results 'Binders targeting cell-surface receptors' "
                                  "and 'Targeting unexplored binding sites'",
                "artifact_sha256": "74bd2902d46460ec387ed6ee46b5bf8fe61b9ea09f2d7be4daa2046ac7e59d5d",
                "review_date": "2026-10-22",
            },
        ],
    },
)

SOURCE_SI = record(
    rid("source", "bindcraft-si"), "source",
    "BindCraft Supplementary Information and Supplementary Data 1 (Pacesa et al., Nature 2025)",
    "Supplementary Information PDF and Supplementary Data 1 retrieved and hashed for the 2026-10-22 "
    "de novo binder design extraction (issue #176).",
    facets=facets(),
    attributes={
        "url": "https://doi.org/10.1038/s41586-025-09429-6",
        "artifact_url": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12507698/supplementaryFiles",
        "version": "Supplementary files archive for PMC12507698, holding "
                   "41586_2025_9429_MOESM1_ESM.pdf (Supplementary Text, Figs. 1-6, Table 1 and "
                   "References) and 41586_2025_9429_MOESM4_ESM.csv (Supplementary Data 1)",
        "retrieved_at": "2026-10-22T12:00:00Z",
        "artifact_sha256": "a402ac50b4860e24430494cb4344c569bf29ef3b8e769372adcd3298659267de",
        "doi": "10.1038/s41586-025-09429-6",
        "publication_status": "peer_reviewed",
        "licence": "CC-BY-NC-ND-4.0",
        "media_type": "application/zip",
        "source_locator": "Supplementary Table 1 (Supplementary Information, page 12); Supplementary "
                          "Data 1",
        "retrieval_method": "Europe PMC REST supplementaryFiles endpoint; the archive was unzipped and "
                            "the Supplementary Information PDF read with pdftotext -layout.",
        "hash_scope": "SHA-256 of one retrieval of the whole supplementary archive. Member hashes: "
                      "Supplementary Information PDF and Supplementary Data 1 CSV were read from this "
                      "archive without re-download.",
        "limitations": [
            "Supplementary Table 1 records design inputs, not measured outcomes.",
            "In the PDF text layer the superscript reference markers are glued to the PDB accessions "
            "('2LAG15' is PDB 2LAG with reference 15). The accessions are transcribed as printed.",
        ],
    },
)

PIPELINE = record(
    rid("pipeline", "bindcraft"), "pipeline", "BindCraft",
    "BindCraft hallucinates a binder backbone and sequence by backpropagating through AlphaFold2 "
    "multimer, redesigns the binder core and surface with a solubility-weighted ProteinMPNN, and "
    "filters the designs on AlphaFold2 monomer and Rosetta scores.",
    facets=facets(method_types=["specialist"]),
    source_ids=[SOURCE["id"]],
    attributes={
        "reported_name": "BindCraft",
        "version": "As published in Nature 2025 (doi 10.1038/s41586-025-09429-6)",
        "access": "Open pipeline; the paper describes an automated single workflow.",
        "provenance_note": "Created from the BindCraft paper for the 2026-10-22 binder design pass.",
        "source_locator": "Fig. 1a; Results 'Accurate design of de novo binders'; Methods",
    },
)

CONFIG = record(
    rid("config", "bindcraft", "default"), "configuration",
    "BindCraft default settings",
    "BindCraft run with the published default settings: AlphaFold2 multimer models 1-5 for design, "
    "ProteinMPNN with solubility weights for core and surface redesign, and AlphaFold2 monomer "
    "reprediction with the default confidence and Rosetta filters.",
    facets=facets(method_types=["specialist"]),
    source_ids=[SOURCE["id"]],
    links=[link("configuration_of", PIPELINE["id"]), link("uses_model", "discovery-model-proteinmpnn")],
    attributes={
        "reported_name": "BindCraft",
        "version": "Nature 2025 version of record",
        "parameters": (
            "AlphaFold2 multimer models 1-5 for design with target flexibility; negative helicity loss "
            "default -0.3; MPNNsol core and surface redesign with the interface kept intact; AlphaFold2 "
            "monomer model 1 reprediction; AF2 confidence plus Rosetta physics filters. The design "
            "pipeline is run for 200 trajectories or until 100 designs pass the in silico filters, and "
            "about 10 designs from the top 20 by i_pTM are picked for experimental testing."
        ),
        "selection": "About 10 designs from the top 20 ranked by i_pTM are chosen for testing.",
        "access_reuse": "Run by the pipeline's own authors.",
        "method_role": "design",
        "foundation_model_eligible": False,
        "source_locator": "Methods 'Binder design'; Results 'Accurate design of de novo binders'",
    },
)

# Supplementary Table 1, every row, transcribed as printed.
SUPP_TABLE_1 = {
    "pd1": ("PD-1", "AF2 prediction, trimmed to 32-146", "64, 126, 129, 133", "80-150"),
    "pdl1": ("PD-L1", "AF2 prediction, trimmed to 18-132", "54, 56, 66, 115", "65-155"),
    "ifnar2": ("IFNAR2", "2LAG15, trimmed to 8-110", "52, 80, 82, 84, 96, 98", "60-175"),
    "cd45": ("CD45", "AF2 prediction of 5FMV16, split by extracellular fibronectin domains",
             "d1, d2, d3, d4, d1-d2, d2-d3, d3-d4", "80-200"),
    "cldn1": ("Claudin1", "AF2 prediction of CLN1-147", "31, 46, 55, 152", "80-175"),
    "bbf14": ("BBF-14", "9HAG7", "None", "70-250"),
    "crsas6": ("CrSAS-6", "AF2 prediction, trimmed to 15-160", "None", "90-200"),
    "derf7": ("Der f7", "AF2 prediction with 3UV1 template17", "132 or 178 or 201", "70-185"),
    "derf21": ("Der f21", "AF2 dimer prediction with 5YNY template18, trimmed to 25-136",
               "34 or 52 or 87 or 105 or 116", "70-185"),
    "betv1": ("Bet v1", "AF2 prediction", "24", "70-185"),
    "spcas9": ("SpCas9", "AF2 prediction with 4ZT0 template, trimmed to 96-174 + 306-446", "360",
               "70-150"),
    "cbago": ("CbAgo",
              "AF2 prediction with 6QZK template20, trimmed to 1-175 + 298-343 + 635-689 (N+PIWI) or "
              "180-276 (PAZ)", "39 (N+PIWI) or 268 (PAZ)", "70-160"),
    "her2aav": ("HER2 (AAV)", "1N8Z21, trimmed to 23-268", "170 or 170, 165", "60-100"),
    "pdl1aav": ("PD-L1 (AAV)", "AF2 prediction, trimmed to 18-132", "54, 56, 58, 63, 66, 113, 115",
                "75-115"),
}

TARGET_DETAIL = {
    "pd1": "Human programmed cell death protein 1, an immune checkpoint receptor on T cells",
    "pdl1": "Programmed death-ligand 1",
    "ifnar2": "Interferon alpha/beta receptor subunit 2",
    "cd45": "CD45 extracellular region, four immunoglobulin-like domains with heavy N-glycosylation",
    "cldn1": "A designed soluble analogue of claudin 1 (sCLDN1-14 and sCLDN1-18)",
    "bbf14": "BBF-14, a de novo designed beta-barrel fold with no natural sequence homologues",
    "crsas6": "CrSAS-6, a conserved centriole structural protein",
    "derf7": "Dust mite allergen Der f 7",
    "derf21": "Dust mite allergen Der f 21",
    "betv1": "Birch allergen Bet v 1",
    "spcas9": "The bipartite REC1 domain of Streptococcus pyogenes Cas9",
    "cbago": "Clostridium butyricum Argonaute, N-PIWI channel or PAZ domain",
    "her2aav": "HER2, targeted for AAV capsid retargeting",
    "pdl1aav": "PD-L1, targeted for AAV capsid retargeting",
}

# Results prose. target key -> (binders, designs tested, printed numerator phrase,
#                               printed denominator phrase, locator, assay)
PROSE_COUNTS = [
    ("pd1", 13, 53, "a binding signal for 13 binders", "screened 53 designs",
     "Results 'Binders targeting cell-surface receptors', paragraph 1: 'We purified and screened 53 "
     "designs for binding using biolayer interferometry (BLI) in a bivalent Fc-fusion format. We "
     "observed a binding signal for 13 binders'",
     "BLI, bivalent Fc-fusion format"),
    ("pdl1", 7, 9, "seven showed a binding signal", "tested nine designs against PD-L1",
     "Results 'Binders targeting cell-surface receptors', paragraph 3: 'We tested nine designs against "
     "PD-L1 out of which seven showed a binding signal (Supplementary Fig. 3a)'",
     "SPR prescreen at 10 micromolar against immobilised PD-L1-Fc, then SPR titration"),
    ("ifnar2", 3, 9, "binding for three out of nine designs", "three out of nine designs",
     "Results 'Binders targeting cell-surface receptors', paragraph 3: 'for IFNAR2 we could detect "
     "binding for three out of nine designs (Fig. 1b)'",
     "SPR"),
    ("cd45", 4, 16, "4 showed binding on SPR", "We tested 16 binders experimentally",
     "Results 'Binders targeting cell-surface receptors', last paragraph: 'We tested 16 binders "
     "experimentally, out of which 4 showed binding on SPR (Fig. 1b)'",
     "SPR"),
    ("cldn1", 6, 7, "all except binder17 to bind to sCLDN1-14 and sCLDN1-18",
     "We tested seven binders",
     "Results 'Targeting unexplored binding sites', paragraph 2: 'We tested seven binders and found all "
     "except binder17 to bind to sCLDN1-14 and sCLDN1-18 (Supplementary Fig. 4a)'",
     "SPR prescreen at 10 micromolar against immobilised soluble claudin-1 analogues"),
    ("bbf14", 6, 11, "6 showed binding", "the 11 top-scoring designs",
     "Results 'Targeting unexplored binding sites', paragraph 3: 'We purified the 11 top-scoring "
     "designs from which 6 showed binding (Fig. 1b)'",
     "SPR"),
    ("derf7", 4, 10, "identified 4 binders", "We examined 10 designs against Der f7 experimentally",
     "Results 'Masking allergenic epitopes', paragraph 2: 'We examined 10 designs against Der f7 "
     "experimentally and identified 4 binders (Fig. 1b)'",
     "SPR"),
    ("derf21", 4, 7, "detect binding for four designs by SPR",
     "we evaluated seven binders against Der f21",
     "Results 'Masking allergenic epitopes', paragraph 4: 'we evaluated seven binders against Der f21 "
     "and could detect binding for four designs by SPR (Fig. 1b)'",
     "SPR"),
    ("betv1", 2, 7, "two successful designs", "from seven tested binders",
     "Results 'Masking allergenic epitopes', paragraph 5: 'we identified two successful designs from "
     "seven tested binders against the birch allergen Bet v1 (Fig. 1b)'",
     "SPR"),
    ("spcas9", 6, 6, "All six tested binders bound the full-length apo SpCas9 enzyme",
     "All six tested binders",
     "Results 'Modulating multi-domain nucleases', paragraph 2: 'All six tested binders bound the "
     "full-length apo SpCas9 enzyme (Supplementary Fig. 5a)'",
     "SPR against full-length apo SpCas9"),
]

# Targets with a denominator in the prose but no numerator.
PROSE_DENOMINATOR_ONLY = [
    ("crsas6", 9, "experimentally tested nine top-scoring binders",
     "Results 'Targeting unexplored binding sites', last paragraph: 'Using BindCraft, we generated "
     "several designs and experimentally tested nine top-scoring binders.'"),
    ("cbago", 12, "We tested the effect of 12 binders on CbAgo-mediated tDNA cleavage",
     "Results 'Modulating multi-domain nucleases', paragraph 5: 'We tested the effect of 12 binders on "
     "CbAgo-mediated tDNA cleavage and two binders strongly inhibit CbAgo activity (Fig. 4f)'"),
]

# Best per-target affinity, as printed in the prose.
AFFINITIES = [
    ("pdl1", "615 nM", "615", "nanomolar", "binder4; apparent KD (Kd*) by SPR",
     "Results 'Binders targeting cell-surface receptors', paragraph 3: 'The top performing binder4 "
     "against PD-L1 showed a Kd* of 615 nM'", None),
    ("ifnar2", "260 nM", "260", "nanomolar", "binder5; by SPR",
     "Results 'Binders targeting cell-surface receptors', paragraph 4: 'The top performing binder5 "
     "against IFNAR2 showed an affinity of 260 nM by SPR'", None),
    ("cd45", "14.7 nM", "14.7", "nanomolar", "binder1; by SPR",
     "Results 'Binders targeting cell-surface receptors', last paragraph: 'The best performing binder1 "
     "showed a Kd of 14.7 nM'", None),
    ("bbf14", "20.9 nM", "20.9", "nanomolar", "binder4; by SPR",
     "Results 'Targeting unexplored binding sites', paragraph 3: 'Binder4showed a Kd of 20.9 nM for "
     "BBF-14, as determined by SPR'", None),
    ("crsas6", "5.7 μM", "5.7", "micromolar", "binder4; monomeric form of CrSAS-6",
     "Results 'Targeting unexplored binding sites', last paragraph: 'Binder4 binds with 5.7 μM affinity "
     "to the monomeric form of CrSAS-6'", None),
    ("crsas6", "4.2 μM", "4.2", "micromolar", "binder4; dimeric form of CrSAS-6",
     "Results 'Targeting unexplored binding sites', last paragraph: 'and 4.2 μM affinity to the dimeric "
     "form'", "dimer"),
    ("derf7", "12.8 nM", "12.8", "nanomolar", "binder2; by SPR",
     "Results 'Masking allergenic epitopes', paragraph 2: 'with binder2 showing the highest binding "
     "affinity with a Kd of 12.8 nM'", None),
    ("derf21", "793 nM", "793", "nanomolar", "binder10; apparent affinity by SPR",
     "Results 'Masking allergenic epitopes', paragraph 4: 'The best performing binder10 showed an "
     "apparent affinity of 793 nM'", None),
    ("betv1", "120 nM", "120", "nanomolar", "binder2; by SPR",
     "Results 'Masking allergenic epitopes', paragraph 5: 'Binder2 showed a 120 nM binding affinity by "
     "SPR'", None),
    ("cbago", "5 nM", "5", "nanomolar", "binder2; by BLI",
     "Results 'Modulating multi-domain nucleases', paragraph 5: 'We found that binder2 binds to CbAgo "
     "with a Kd of 5 nM, as determined by BLI'", None),
]

# Affinities the prose states without a number.
AFFINITIES_NON_NUMERIC = [
    ("pd1", "lower than 1 nM", "nanomolar", "binder2; apparent KD (Kd*) by BLI in a bivalent "
     "Fc-fusion format; the exact value could not be determined",
     "Results 'Binders targeting cell-surface receptors', paragraph 1: 'with the best binder showing an "
     "apparent dissociation constant (Kd*) lower than 1 nM (Fig. 2a,b), although the exact Kd could not "
     "be determined due to the extremely slow dissociation rate and avidity effect from the Fc-fusion "
     "construct'"),
    ("spcas9", "in the range of 300 nM", "nanomolar", "binder3 and binder10; apparent affinities by "
     "SPR; complete titration curves were challenging to obtain",
     "Results 'Modulating multi-domain nucleases', paragraph 2: 'The top performing binder3 and 10 "
     "showed apparent binding affinities in the range of 300 nM by SPR, although complete titration "
     "curves were challenging to obtain'"),
]

SCREEN_LIMITS = [
    "Developer-reported: the BindCraft authors built the pipeline, chose the targets and chose which "
    "designs to test.",
    "The assay is not uniform across targets. Fig. 1b's caption says binding was observed on SPR, but "
    "PD-1 was screened by BLI in a bivalent Fc-fusion format and the claudin binders were prescreened "
    "against soluble analogues of the target rather than the wild-type protein.",
    "No numeric binding threshold is stated. A successful design is one where a binding signal was "
    "observed.",
    "Denominators are 6 to 53 designs per target, and the designs tested are about 10 of the top 20 "
    "ranked by the pipeline's own i_pTM filter, so design and selection are coupled.",
    "No conventional comparator (directed evolution, display selection or grafting) was run on these "
    "targets.",
    "No uncertainty is printed.",
    "Two targets, CrSAS-6 and CbAgo, have a stated denominator but no stated numerator in the prose; "
    "their numerators appear only inside the Fig. 1b graphic, which was not read.",
]

PROTOCOLS = {
    "screen": record(
        rid("protocol", "bindcraft", "binding-screen"), "protocol",
        "BindCraft per-target binding screen, hit where a binding signal was observed",
        "Number of tested BindCraft designs for which a binding signal was observed in the paper's "
        "per-target screen, out of the designs tested.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "Designs passing the in silico filters are ranked by i_pTM, about ten of the top twenty "
                "are expressed and purified, and binding to the target is screened by SPR, or by BLI in "
                "a bivalent Fc-fusion format for PD-1, or by SPR against soluble analogues for claudin "
                "1. Fig. 1b reports the number of designs with observed binding against the number "
                "tested."
            ),
            "version": "Nature 2025 version of record; Fig. 1b and the Results prose",
            "metric": "count",
            "metric_direction": "higher",
            "metric_qualifier": "designs with an observed binding signal, out of designs tested",
            "unit": "count",
            "unit_detail": "designs",
            "success_threshold": {
                "criterion": "a binding signal observed in the per-target screen",
                "note": "No numeric affinity or signal threshold is stated, and the assay differs "
                        "between targets.",
                "locator": "Fig. 1b caption",
            },
            "selection": "About 10 designs from the top 20 ranked by i_pTM.",
            "selection_bias": "The ranking that chose the tested designs is the pipeline's own i_pTM "
                              "score, so design and selection are not independent.",
            "source_locator": "Fig. 1b caption; Results sections 'Binders targeting cell-surface "
                              "receptors', 'Targeting unexplored binding sites', 'Masking allergenic "
                              "epitopes' and 'Modulating multi-domain nucleases'",
            "limitations": SCREEN_LIMITS,
        },
    ),
    "aggregate": record(
        rid("protocol", "bindcraft", "mean-success-rate-12-targets"), "protocol",
        "BindCraft experimental success rate averaged over its 12 benchmark targets",
        "Mean and range of the per-target experimental success rate over the 12 targets BindCraft was "
        "benchmarked on.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "Per-target experimental success rates from the Fig. 1b screens, averaged over the 12 "
                "benchmark targets and reported with their range."
            ),
            "version": "Nature 2025 version of record; Introduction",
            "metric": "hit-rate",
            "metric_direction": "higher",
            "metric_qualifier": "mean of per-target experimental success rates over 12 targets",
            "unit": "percent",
            "aggregation": "Unweighted mean over the 12 benchmark targets; each target contributes its "
                           "own rate regardless of how many designs were tested.",
            "denominator": 12,
            "comparison_limit": (
                "An unweighted mean over targets whose denominators range from 6 to 53 designs, and "
                "whose endpoints are not the same assay. It is not a hit rate over a pooled design set."
            ),
            "source_locator": "Introduction, final paragraph",
            "limitations": SCREEN_LIMITS + [
                "An unweighted mean over targets, not a pooled rate over designs. A target where 6 of 6 "
                "designs bound contributes as much as one where 13 of 53 did.",
                "The 12 targets were chosen by the authors.",
            ],
        },
    ),
    "affinity": record(
        rid("protocol", "bindcraft", "best-affinity"), "protocol",
        "BindCraft best per-target binder affinity",
        "Dissociation constant of the highest-affinity BindCraft binder per target, without "
        "experimental sequence optimisation.",
        facets=facets(),
        source_ids=[SOURCE["id"]],
        attributes={
            "protocol": (
                "The best binder identified in the per-target screen is titrated by SPR, or by BLI for "
                "PD-1 and CbAgo, and the dissociation constant is reported. Fig. 1b marks values as "
                "estimated (Kd*) where the fit was poor."
            ),
            "version": "Nature 2025 version of record; Figs. 1b, 2, 3 and 4",
            "metric": "dissociation-constant",
            "metric_direction": "lower",
            "metric_qualifier": "best per-target KD without experimental sequence optimisation",
            "unit": "nanomolar",
            "aggregation": "Minimum over the binders identified for the target.",
            "comparison_limit": (
                "A best-of value over a small selected set. Several values are apparent constants "
                "(Kd*) from poor fits or from a bivalent Fc-fusion construct, which inflates apparent "
                "affinity through avidity, and are not comparable with monovalent fitted constants."
            ),
            "source_locator": "Fig. 1b caption; Figs. 2, 3 and 4; Extended Data Figs. 3 and 5",
            "limitations": [
                "Best-of-subset, not a distribution; no uncertainty is printed.",
                "Mixed assays and mixed construct formats: SPR, BLI, monovalent and bivalent Fc fusion.",
                "Several values are apparent constants (Kd*) rather than fitted monovalent constants.",
                "Developer-reported.",
            ],
        },
    ),
}

XML_METHOD = ["transcription"]
HOW = ("Transcribed by hand from the Europe PMC JATS full text of the pinned article, flattened to "
       "plain text. Each value was located in the Results prose and the surrounding sentence is "
       "quoted in the source locator. Figure 1b's graphic boxes were not read.")
SI_METHOD = ["pdf-text-parse", "transcription"]
SI_HOW = ("Transcribed by hand from the pdftotext -layout text layer of the Supplementary Information "
          "PDF held in the pinned supplementary archive.")

DATASETS = {}
for key, (printed, pdb, hotspots, length) in SUPP_TABLE_1.items():
    DATASETS[key] = record(
        rid("data", "bindcraft", key), "dataset",
        f"BindCraft binder design target {printed}",
        f"{TARGET_DETAIL[key]}, used as the BindCraft design target with the input structure, hotspot "
        f"settings and binder length given in Supplementary Table 1.",
        facets=facets(),
        source_ids=[SOURCE["id"], SOURCE_SI["id"]],
        attributes={
            "reported_name": printed,
            "version": "Supplementary Table 1, Nature 2025 version of record",
            "scope_note": (
                f"Supplementary Table 1, row '{printed}': input PDB '{pdb}'; hotspots '{hotspots}'; "
                f"binder length '{length}'. In the PDF text layer the superscript reference markers are "
                f"glued to the accessions and are transcribed as printed."
            ),
            "population": f"BindCraft designs generated against {printed}, {length} residues long",
            "source_locator": f"Supplementary Table 1, row '{printed}'",
            "missing_metadata": {
                "accession": {
                    "reason": "unreported",
                    "note": "Several inputs are AlphaFold2 predictions rather than a deposited "
                            "structure, so no single accession identifies the target used.",
                },
            },
        },
    )

DATASETS["twelve"] = record(
    rid("data", "bindcraft", "twelve-benchmark-targets"), "dataset",
    "BindCraft 12-target benchmark set",
    "The twelve targets BindCraft was benchmarked on: PD-1, PD-L1, IFNAR2, CD45, a soluble claudin-1 "
    "analogue, BBF-14, CrSAS-6, Der f7, Der f21, Bet v1, the SpCas9 REC1 domain and CbAgo.",
    facets=facets(),
    source_ids=[SOURCE["id"], SOURCE_SI["id"]],
    attributes={
        "reported_name": "12 targets",
        "version": "Nature 2025 version of record; Supplementary Table 1",
        "total_targets": 12,
        "population": "Twelve targets chosen by the authors, spanning cell-surface receptors, a "
                      "membrane-protein soluble analogue, a de novo designed beta barrel, three "
                      "allergens and two nucleic-acid-guided nucleases.",
        "scope_note": "Supplementary Table 1 lists fourteen rows; the two AAV rows (HER2 (AAV) and "
                      "PD-L1 (AAV)) belong to the AAV retargeting application, not the 12-target "
                      "benchmark.",
        "source_locator": "Results 'Accurate design of de novo binders': 'We benchmarked BindCraft on "
                          "12 targets to assess its generalizability (Fig. 1b)'",
    },
)


def build():
    out = [SOURCE, SOURCE_SI, PIPELINE, CONFIG]
    out += list(DATASETS.values())
    out += list(PROTOCOLS.values())
    rev = review(SOURCE, XML_METHOD, HOW)
    rev_si = review(SOURCE_SI, SI_METHOD, SI_HOW)

    def screen_eval(key, tested, locator, assay, numerator=None):
        printed = SUPP_TABLE_1[key][0]
        ev_id = rid("eval", "bindcraft", "screen", key)
        out.append(evaluation(
            ev_id,
            f"BindCraft binding screen against {printed}",
            "Developer-reported outcome transcribed from the pinned source; not reproduced.",
            source=SOURCE, system=CONFIG["id"], assessment=PROTOCOLS["screen"]["id"],
            data=DATASETS[key]["id"],
            origin="author_reported", version="Nature 2025 version of record",
            comparison=comparison(
                PROTOCOLS["screen"]["id"],
                dataset_version=f"{printed}, Supplementary Table 1 input",
                population=f"{tested} BindCraft designs tested against {printed}",
                inputs="Target structure and hotspot residues from Supplementary Table 1",
                metric_implementation=f"Count of tested designs with an observed binding signal "
                                      f"({assay})",
                aggregation="Count per target",
                budget=f"{tested} designs expressed, purified and assayed",
            ),
            locator=locator,
            attrs={
                "denominator": tested,
                "endpoint": f"Binding signal observed by {assay}",
                "candidate_selection": "About 10 designs from the top 20 ranked by the pipeline's own "
                                       "i_pTM score.",
                "conventional_baseline": "None run on this target.",
            },
            missing=missing(
                comparison__split=("inapplicable", "A design campaign, not a train/test split."),
                comparison__adaptation=("inapplicable", "No adaptation step."),
            ),
        ))
        return ev_id

    for key, binders, tested, num_phrase, den_phrase, locator, assay in PROSE_COUNTS:
        printed = SUPP_TABLE_1[key][0]
        ev_id = screen_eval(key, tested, locator, assay)
        out.append(result(
            rid("result", "bindcraft", "binders", key),
            f"BindCraft designs with observed binding against {printed}",
            "Developer-reported count transcribed from the pinned source. Not reproduced.",
            source=SOURCE, evaluation_id=ev_id, printed=num_phrase, numeric=str(binders),
            metric="count", direction="higher", unit="count",
            qualifier=f"designs with an observed binding signal ({assay}), out of designs tested",
            unit_detail="designs",
            numerator=binders, denominator=tested,
            denominator_note=f"{tested} designs tested, from the same sentence: '{den_phrase}'.",
            locator=locator, review_block=rev,
            extra={
                "printed_value_basis": "The count is stated in the Results prose in words or digits; "
                                       "the quoted phrase is the printed form. The paper prints no "
                                       "per-target rate.",
            },
            missing=missing(uncertainty=("inapplicable", "An exact count.")),
        ))

    for key, tested, den_phrase, locator in PROSE_DENOMINATOR_ONLY:
        screen_eval(key, tested, locator, "SPR")

    # The aggregate mean and range.
    ev_agg = rid("eval", "bindcraft", "aggregate", "12-targets")
    out.append(evaluation(
        ev_agg,
        "BindCraft experimental success rate over its 12 benchmark targets",
        "Developer-reported aggregate transcribed from the pinned source; not reproduced.",
        source=SOURCE, system=CONFIG["id"], assessment=PROTOCOLS["aggregate"]["id"],
        data=DATASETS["twelve"]["id"],
        origin="author_reported", version="Nature 2025 version of record",
        comparison=comparison(
            PROTOCOLS["aggregate"]["id"],
            dataset_version="12 targets, Supplementary Table 1 inputs",
            population="12 targets; 6 to 53 designs tested per target",
            inputs="Target structures and hotspot residues from Supplementary Table 1",
            metric_implementation="Per-target share of tested designs with observed binding",
            aggregation="Unweighted mean over the 12 targets",
        ),
        locator="Introduction, final paragraph",
        attrs={
            "total_targets": 12,
            "conventional_baseline": "None run on these targets.",
        },
        missing=missing(
            comparison__split=("inapplicable", "A design campaign, not a train/test split."),
            comparison__adaptation=("inapplicable", "No adaptation step."),
            comparison__budget=("conflicting",
                "Designs tested per target range from 6 to 53 and the mean is unweighted, so no single "
                "budget describes the aggregate."),
        ),
    ))
    out.append(result(
        rid("result", "bindcraft", "mean-success-rate"),
        "BindCraft average experimental success rate over 12 targets",
        "Developer-reported value transcribed from the pinned source. Not reproduced.",
        source=SOURCE, evaluation_id=ev_agg, printed="46.3%", numeric="46.3",
        metric="hit-rate", direction="higher", unit="percent",
        qualifier="unweighted mean of per-target experimental success rates over 12 targets",
        unit_detail="percent of designs tested, averaged over targets",
        denominator=12,
        denominator_note="12 targets. Per-target design denominators range from 6 to 53 and are not "
                         "pooled; each target contributes its own rate to the mean.",
        locator="Introduction, final paragraph: 'The binder affinities lie predominantly in the "
                "nanomolar range, with success rates from 10% to 100%, with an average success rate of "
                "46.3%'",
        review_block=rev,
        missing=missing(uncertainty=("unreported", "No interval is printed.")),
    ))
    out.append(result(
        rid("result", "bindcraft", "success-rate-range"),
        "BindCraft per-target experimental success rate range over 12 targets",
        "Developer-reported range transcribed from the pinned source. Not reproduced.",
        source=SOURCE, evaluation_id=ev_agg, printed="10% to 100%", numeric=None,
        metric="hit-rate", direction="higher", unit="percent",
        qualifier="range of per-target experimental success rates over 12 targets",
        unit_detail="percent of designs tested",
        denominator=12,
        denominator_note="12 targets; the range is over targets, not over designs.",
        locator="Introduction, final paragraph: 'with success rates from 10% to 100%'",
        review_block=rev,
        extra={
            "printed_value_basis": "A range over the 12 targets, printed in the introduction as '10% "
                                   "to 100%'. It is not a confidence interval and not a single value, "
                                   "so numeric_value is null.",
            "scope_note": "The lowest per-target rate printed anywhere in the paper is 10% and the "
                          "highest is 100%; the range is over targets, not over designs.",
        },
        missing=missing(uncertainty=("inapplicable",
                                     "The value is itself a range over targets, not an estimate with "
                                     "an interval.")),
    ))

    # Best per-target affinities.
    seen = set()
    for key, printed, numeric, unit, qualifier, locator, suffix in AFFINITIES:
        printed_target = SUPP_TABLE_1[key][0]
        tag = key if suffix is None else f"{key}-{suffix}"
        ev_id = rid("eval", "bindcraft", "affinity", tag)
        if ev_id not in seen:
            seen.add(ev_id)
            out.append(evaluation(
                ev_id,
                f"BindCraft best binder affinity against {printed_target}"
                + (f" ({suffix})" if suffix else ""),
                "Developer-reported outcome transcribed from the pinned source; not reproduced.",
                source=SOURCE, system=CONFIG["id"], assessment=PROTOCOLS["affinity"]["id"],
                data=DATASETS[key]["id"],
                origin="author_reported", version="Nature 2025 version of record",
                comparison=comparison(
                    PROTOCOLS["affinity"]["id"],
                    dataset_version=f"{printed_target}, Supplementary Table 1 input",
                    inputs="Target structure and hotspot residues from Supplementary Table 1",
                    metric_implementation=qualifier,
                    aggregation="Best (lowest) KD among the binders identified for the target",
                ),
                locator=locator,
                attrs={"conventional_baseline": "None run on this target."},
                missing=missing(
                    comparison__split=("inapplicable", "A design campaign, not a train/test split."),
                    comparison__population=("unreported",
                        "The paper does not state how many of the target's binders were titrated."),
                    comparison__adaptation=("inapplicable",
                        "Affinities are for designs without experimental sequence optimisation."),
                    comparison__budget=("unreported", "Not stated for the titration step."),
                ),
            ))
        out.append(result(
            rid("result", "bindcraft", "kd", tag),
            f"BindCraft best binder affinity against {printed_target}"
            + (f" ({suffix})" if suffix else ""),
            "Developer-reported value transcribed from the pinned source. Not reproduced.",
            source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=numeric,
            metric="dissociation-constant", direction="lower", unit=unit,
            qualifier=qualifier, locator=locator, review_block=rev,
            missing=missing(uncertainty=("unreported", "No interval is printed.")),
        ))

    for key, printed, unit, qualifier, locator in AFFINITIES_NON_NUMERIC:
        printed_target = SUPP_TABLE_1[key][0]
        ev_id = rid("eval", "bindcraft", "affinity", key)
        out.append(evaluation(
            ev_id,
            f"BindCraft best binder affinity against {printed_target}",
            "Developer-reported outcome transcribed from the pinned source; not reproduced.",
            source=SOURCE, system=CONFIG["id"], assessment=PROTOCOLS["affinity"]["id"],
            data=DATASETS[key]["id"],
            origin="author_reported", version="Nature 2025 version of record",
            comparison=comparison(
                PROTOCOLS["affinity"]["id"],
                dataset_version=f"{printed_target}, Supplementary Table 1 input",
                inputs="Target structure and hotspot residues from Supplementary Table 1",
                metric_implementation=qualifier,
                aggregation="Best KD among the binders identified for the target",
            ),
            locator=locator,
            attrs={"conventional_baseline": "None run on this target."},
            missing=missing(
                comparison__split=("inapplicable", "A design campaign, not a train/test split."),
                comparison__population=("unreported",
                    "The paper does not state how many of the target's binders were titrated."),
                comparison__adaptation=("inapplicable",
                    "Affinities are for designs without experimental sequence optimisation."),
                comparison__budget=("unreported", "Not stated for the titration step."),
            ),
        ))
        out.append(result(
            rid("result", "bindcraft", "kd", key),
            f"BindCraft best binder affinity against {printed_target} (no numeric value printed)",
            "Developer-reported value transcribed from the pinned source. The source does not print a "
            "number, so numeric_value is null.",
            source=SOURCE, evaluation_id=ev_id, printed=printed, numeric=None,
            metric="dissociation-constant", direction="lower", unit=unit,
            qualifier=qualifier, locator=locator, review_block=rev,
            extra={"printed_value_basis": "The source states a bound or an approximate range in words "
                                          "rather than a fitted value."},
            missing=missing(uncertainty=("unreported", "No interval is printed.")),
        ))

    out.append(claim(
        rid("claim", "bindcraft", "supplementary-data-1-ambiguous-filter"),
        "BindCraft Supplementary Data 1 does not let the per-target hit counts be recomputed",
        "Supplementary Data 1 holds one row per tested design with a Binding column of 1, 0 or an empty "
        "cell. Treating the non-empty cells as the tested set reconciles with the Results prose for "
        "nine of twelve targets and not for PD-L1, CrSAS-6 or CbAgo, so the row filter is ambiguous and "
        "no value is computed from these rows.",
        source=SOURCE_SI, subject=PIPELINE["id"], field="supplementary_data_reconciliation",
        value=(
            "Supplementary Data 1 (41586_2025_9429_MOESM4_ESM.csv) has 211 design rows across 13 target "
            "labels. Rows with a non-empty Binding cell, and the count of Binding = 1, against the "
            "prose: BBF-14 11 and 6 against 11 tested and 6 binding; Bet v1 7 and 2 against 7 and 2; "
            "CD45 16 and 4 against 16 and 4; Der f7 10 and 4 against 10 and 4; Der f21 7 and 4 against "
            "7 and 4; IFNAR2 9 and 3 against 9 and 3; PD-1 53 and 13 against 53 and 13; SpCas9 6 and 6 "
            "against 6 and 6; CLDN1 7 and 6 against 7 and 6; PD-L1 13 and 11 against 9 tested and 7 "
            "binding; CrSAS-6 10 and 3 against 9 tested with no numerator in the prose; CbAgo 2 and 2 "
            "against 12 tested with no numerator in the prose. HER2 has 1 non-empty row and belongs to "
            "the AAV application. The three mismatches mean the filter the figure's aggregation implies "
            "cannot be applied to these rows, so under docs/collection.md the per-target counts for "
            "PD-L1, CrSAS-6 and CbAgo are recorded as a gap rather than computed."
        ),
        locator="Supplementary Data 1 (41586_2025_9429_MOESM4_ESM.csv), columns Target, DesignName, "
                "Binding; Fig. 1b caption; Results prose",
        review_block=rev_si,
        source_ids=[SOURCE_SI["id"], SOURCE["id"]],
    ))

    out.append(claim(
        rid("claim", "bindcraft", "target-input-provenance"),
        "Most BindCraft targets were designed against a predicted structure, not a deposited complex",
        "Supplementary Table 1 shows that nine of the twelve benchmark targets were designed against an "
        "AlphaFold2 prediction, in four cases with a PDB template, and three against a deposited "
        "structure. None of the inputs is a solved complex with a known binder, so the target inputs do "
        "not carry a known binding partner.",
        source=SOURCE_SI, subject=DATASETS["twelve"]["id"], field="target_input_provenance",
        value=(
            "Supplementary Table 1, input structures as printed: PD-1 'AF2 prediction, trimmed to "
            "32-146'; PD-L1 'AF2 prediction, trimmed to 18-132'; IFNAR2 '2LAG15, trimmed to 8-110'; "
            "CD45 'AF2 prediction of 5FMV16, split by extracellular fibronectin domains'; Claudin1 "
            "'AF2 prediction of CLN1-147'; BBF-14 '9HAG7'; CrSAS-6 'AF2 prediction, trimmed to 15-160'; "
            "Der f7 'AF2 prediction with 3UV1 template17'; Der f21 'AF2 dimer prediction with 5YNY "
            "template18, trimmed to 25-136'; Bet v1 'AF2 prediction'; SpCas9 'AF2 prediction with 4ZT0 "
            "template, trimmed to 96-174 + 306-446'; CbAgo 'AF2 prediction with 6QZK template20, "
            "trimmed to 1-175 + 298-343 + 635-689 (N+PIWI) or 180-276 (PAZ)'; HER2 (AAV) '1N8Z21, "
            "trimmed to 23-268'; PD-L1 (AAV) 'AF2 prediction, trimmed to 18-132'. Superscript reference "
            "markers are glued to the accessions in the PDF text layer and are transcribed as printed."
        ),
        locator="Supplementary Table 1, column 'Input PDB'",
        review_block=rev_si,
    ))

    return out
