"""Extract the AlphaGenome Atlas preprint (medRxiv 10.64898/2026.09.16.26363192 v1) into a needs_review batch.

Usage:
  python3 -I extract/build_batch.py <artifact-dir> <batch-folder>

<artifact-dir> holds the pinned PDF as atlas-v1.full.pdf. Its hash is asserted before anything is read.
Prose values and figure-legend values are asserted as exact substrings of the whitespace-flattened
`pdftotext -layout` text. Table S2 is parsed from the same text with every row label and column header
asserted. Fig. 2A and 2B bar labels are not extracted: the bars carry no predictor labels and are told
apart only by colour, so only values the text names are recorded. Existing records are reused, never
changed. All records are written with status needs_review.
"""
import csv, hashlib, json, os, re, subprocess, sys

TODAY = "2026-10-19"
P = "ag-atlas-20261019"
PDF = "atlas-v1.full.pdf"
PDF_SHA = "b32d1539005ca4ea31c3dcef49b834424b1d8b5da4ce6b9fc3e1f942d39fc453"
PDF_URL = "https://www.medrxiv.org/content/10.64898/2026.09.16.26363192v1.full.pdf"
RETRIEVED = "2026-10-19T12:19:03Z"
EXTRACTOR_NOTE = ("Extractor: Claude (Opus 5.5) automated research agent; extraction only, not independent review; "
                  "no human review claimed.")
AREAS = ["dna-genomes"]

# Existing records reused (never changed).
M_AG = "catalog-model-alphagenome"
M_AM = "somatic-oncogenicity-20261009-method-alphamissense"
M_CADD = "somatic-oncogenicity-20261009-method-cadd"
M_PHYLOP = "somatic-oncogenicity-20261009-method-phylop"
M_PHASTCONS = "somatic-oncogenicity-20261009-method-phastcons"
M_GPNSTAR = "vep-uc-20261014-model-gpn-star"
M_SPLICEAI = "catalog-model-spliceai"
M_PANGOLIN = "catalog-model-pangolin"
D_TG_COMPLEX = "lit-genomics-20261011-traitgym-data-complex-traits-matched-9"
D_TG_MENDELIAN = "lit-genomics-20261011-traitgym-data-mendelian-traits-matched-9"

S = P + "-source-preprint"
PDF_PARSE = ["pdf-text-parse", "transcription"]
TABLE_PARSE = ["pdf-text-parse", "deterministic-table-parse"]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def flat(s):
    return " ".join(s.split())


def need(text, phrase):
    assert flat(phrase) in text, f"phrase not found: {phrase[:90]}"
    return phrase


def num(printed):
    t = printed.strip().rstrip("%")
    return t if re.fullmatch(r"-?\d+(\.\d+)?", t) else None


class Batch:
    def __init__(self):
        self.records, self.ids, self.rows = [], set(), []

    def add(self, rec):
        assert rec["id"] not in self.ids, rec["id"]
        self.ids.add(rec["id"])
        mm = rec["attributes"].get("missing_metadata")
        if mm:
            rec["attributes"]["missing_metadata"] = dict(sorted(mm.items()))
        self.records.append(rec)
        return rec["id"]

    def entity(self, kind, id, name, description, attrs, links=(), method_types=None, contexts=("research",)):
        facets = {"areas": AREAS, "contexts": list(contexts)}
        if method_types:
            facets["method_types"] = method_types
        return self.add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                         "facets": facets, "source_ids": [S], "links": list(links), "attributes": attrs})

    def review(self, methods, note):
        return {"method": methods, "method_note": note, "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE,
                "date": TODAY, "artifact_sha256": PDF_SHA, "retrieval_url": PDF_URL,
                "note": "Extraction only; pending independent review. The review-evidence pass must re-check this value against the pinned artifact."}

    def claim(self, key, name, subject, field, value, locator, methods, note, limitations=None):
        id = f"{P}-claim-{key}"
        attrs = {"field": field, "value": value, "source_locator": locator, "review": self.review(methods, note)}
        if limitations:
            attrs["limitations"] = limitations
        self.rows.append([id, S, locator, value[:200], "claim"])
        return self.add({"id": id, "kind": "claim", "name": name, "description": "Descriptive fact transcribed from the pinned source.",
                         "status": "needs_review", "facets": {}, "source_ids": [S],
                         "links": [{"relation": "subject", "target_id": subject}], "attributes": attrs})

    def result(self, id, name, evaluation, printed, metric, unit, locator, methods, note, qualifier, uncertainty_note=None,
               extra=None):
        mm = {"uncertainty": {"reason": "unreported"}}
        if uncertainty_note:
            mm["uncertainty"]["note"] = uncertainty_note
        attrs = {"metric": metric, "metric_direction": "higher", "unit": unit, "printed_value": printed,
                 "numeric_value": num(printed), "metric_qualifier": qualifier, "source_locator": locator,
                 "missing_metadata": mm, "review": self.review(methods, note)}
        assert attrs["numeric_value"] is not None, printed
        attrs.update(extra or {})
        self.rows.append([id, S, locator, printed, "result"])
        return self.add({"id": id, "kind": "result", "name": name,
                         "description": "Developer-reported value transcribed from the pinned source. Not independently reproduced.",
                         "status": "needs_review", "facets": {}, "source_ids": [S],
                         "links": [{"relation": "evaluation", "target_id": evaluation}], "attributes": attrs})

    def evaluation(self, id, name, system, protocol, data, comparison, locator, extra=None, missing=None):
        attrs = {"origin": "author_reported", "protocol": protocol, "version": "medRxiv v1, retrieved " + TODAY,
                 "comparison": dict(comparison, protocol_id=protocol), "source_locator": locator}
        mm = {f"comparison.{k}": {"reason": "unreported"} for k, v in comparison.items() if v is None}
        mm.update(missing or {})
        if mm:
            attrs["missing_metadata"] = mm
        attrs.update(extra or {})
        return self.entity("evaluation", id, name, "Developer-reported comparison transcribed from the pinned source; not reproduced.",
                           attrs, links=[{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                                         {"relation": "data", "target_id": data}], contexts=("clinical_research",))


def build(b, text, layout):
    # ------------------------------------------------------------------ source
    b.add({"id": S, "kind": "source",
           "name": "AlphaGenome Atlas: in silico mutagenesis of the entire human genome (Cheng, Taylor, Nicolaisen et al., medRxiv 2026)",
           "description": "Primary source retrieved and hashed for the 2026-10-19 AlphaGenome variant evidence extraction.",
           "status": "needs_review", "facets": {"areas": AREAS, "contexts": ["research", "clinical_research"]}, "source_ids": [], "links": [],
           "attributes": {
               "url": "https://doi.org/10.64898/2026.09.16.26363192", "artifact_url": PDF_URL, "doi": "10.64898/2026.09.16.26363192",
               "version": "medRxiv preprint version 1, posted 2026-09-20; full-text PDF with supplementary figures and tables (53 pages)",
               "retrieved_at": RETRIEVED, "artifact_sha256": PDF_SHA, "publication_status": "preprint", "licence": "CC-BY-NC-4.0",
               "media_type": "application/pdf",
               "source_locator": "Main text Fig. 2 and 3 and their Results paragraphs; Materials and methods; fig. S7 and S9; Tables S1 and S2",
               "hash_scope": ("SHA-256 of one retrieval of the medRxiv PDF. A second retrieval at 2026-10-19T12:30:54Z had the same "
                              "length (15,415,633 bytes) and the same SHA-256."),
               "limitations": [
                   "Preprint, not peer reviewed (medRxiv v1; the medRxiv API 'published' field was not checked against a journal version).",
                   "Developer study: the AlphaGenome Atlas team is led by Google DeepMind, which also develops AlphaGenome and AlphaMissense. All "
                   "evaluations, including those of comparator methods, were run by the authors.",
                   "Fig. 2A and 2B print bar labels but identify the predictor of each bar only by colour; those labels are not extracted. "
                   "Only values the text attributes to a named method, and figure legends that name the method, are recorded.",
                   "No numeric confidence intervals are printed. Fig. 2 error bars are 95% bootstrap intervals (100 bootstraps) drawn without values.",
                   "Data S1 (DNM1 screen) and the precomputed Atlas scores were not retrieved.",
               ],
               "missing_metadata": {"artifact_member": {"reason": "inapplicable", "note": "Single PDF; supplementary material is inside it."}},
           }})

    # ------------------------------------------------------------------ AVI pipeline and configurations
    need(text, "We grouped AlphaGenome predictions into ten different features based on the assay modality")
    need(text, "four coding features consisting of AlphaMissense and three VEP protein termination features")
    need(text, "AVI was trained to discriminate between observed human variants that have a filtering allele frequency above or below 0.1%")
    avi = b.entity("pipeline", P + "-pipeline-avi", "AlphaGenome Variant Impact (AVI)",
                   "Scores the impact of SNVs and indels with a small neural network over 18 features: ten AlphaGenome modality scores, "
                   "AlphaMissense, two conservation scores, three VEP loss-of-function indicators and two indel-type indicators, trained "
                   "to separate rare from common gnomAD variants.",
                   {"configuration_type": "pipeline", "reported_name": "AVI (AlphaGenome Variant Impact)",
                    "version": "AlphaGenome Atlas medRxiv v1",
                    "parameters": ("Inputs: AlphaGenome scores (10 features: ATAC, contact maps, DNase, ChIP-TF, ChIP-histone, CAGE, PRO-cap, RNA-seq, "
                                   "polyadenylation and one merged splicing score, each the maximum absolute value over tracks and genes, active-allele "
                                   "scorers excluded); AlphaMissense (1); Zoonomia Cactus 241-way phyloP (1); PhastCons 470-way (1); VEP protein "
                                   "termination, stop lost and start lost indicators (3); insertion and deletion indicators (2). Labels: gnomAD v4.1 "
                                   "genome FAF95_GRPMAX above versus below 0.1% (proxy neutral versus proxy impactful), trinucleotide-matched balanced "
                                   "sampling. Training chromosomes 1, 4, 7, 8, 10, 13 and 15. Raw logits converted to PHRED scores."),
                    "access": "Precomputed AVI scores and feature attributions through an API and https://alphagenome.google/atlas",
                    "source_locator": "Results 'Whole genome in silico mutagenesis...' paragraph 2; Methods 'AlphaGenome Variant Impact Scores' (pages 20 to 26)",
                    "provenance_note": "Introduced in the AlphaGenome Atlas preprint (medRxiv v1). The checkpoint files are not published in the paper."},
                   links=[{"relation": "uses_model", "target_id": M_AG}, {"relation": "uses_model", "target_id": M_AM},
                          {"relation": "uses_model", "target_id": M_PHYLOP}, {"relation": "uses_model", "target_id": M_PHASTCONS}],
                   method_types=["supervised_machine_learning"])

    need(text, "The final model was an ensemble of six models selected from a large hyperparameter sweep over 10 resampled datasets")
    avi_cfg = b.entity("configuration", P + "-config-avi-ensemble", "AVI six-model ensemble (AlphaGenome Atlas v1)",
                       "Six AVI models (linear model plus linear hypernetwork plus indel embedding) whose logits are averaged; scores reported as raw logits or PHRED.",
                       {"reported_name": "AVI", "version": "AlphaGenome Atlas medRxiv v1 ensemble",
                        "parameters": ("Ensemble of six models chosen by validation AUPRC from a sweep over 10 resampled datasets and 50 seeds; "
                                       "hidden layers 2x16 or 2x32, exponential or softplus weight activation, additive bias gating on or off. "
                                       "At inference, indel AlphaMissense is imputed as the mean SNV AlphaMissense score over the affected interval. "
                                       "Checkpoint selection on the average validation AUPRC of TraitGym Complex Traits, SGE SNVs and SGE indels."),
                        "training_overlap": ("Benchmark variants whose position overlaps any AVI training or validation variant are removed for every "
                                             "method; comparator training sets were not filtered."),
                        "source_locator": "Methods 'Ensemble Models', 'Training Procedure', 'Overlap Filtering during Evaluation' (pages 22 to 25)",
                        "missing_metadata": {"checkpoint": {"reason": "unavailable", "note": "No checkpoint identifier or weights link printed."}}},
                       links=[{"relation": "configuration_of", "target_id": avi}], method_types=["supervised_machine_learning"])

    need(text, "both the AlphaGenome merged splicing score (Methods, AUPRC: 0.943) and the AVI splicing feature attributions (AUPRC: 0.943)")
    avi_shap = b.entity("configuration", P + "-config-avi-splicing-shap", "AVI splicing-feature SHAP attribution (AlphaGenome Atlas v1)",
                        "Scores a variant by the SHAP contribution of the AlphaGenome merged splicing feature to its AVI score, computed with expected gradients against a zero background.",
                        {"reported_name": "AVI Splicing SHAP attribution",
                         "parameters": "shap.GradientExplainer (expected gradients) with a single all-zero background vector; splicing feature attribution only",
                         "source_locator": "Methods 'Feature Attribution Analysis' (page 25); fig. S9E legend"},
                        links=[{"relation": "configuration_of", "target_id": avi}, {"relation": "uses_model", "target_id": M_AG}],
                        method_types=["supervised_machine_learning"])

    # ------------------------------------------------------------------ AlphaGenome merged splicing score
    need(text, "using the AlphaGenome distilled model (9). All variant scores were computed on the GRCh38 (hg38) reference genome assembly using GENCODE v46 gene annotations.")
    need(text, "The interval is then expanded to 1 Mb from the window’s interval center")
    need(text, "where each component is the maximum score observed across all coordinates and genes.")
    ag_splice = b.entity("configuration", P + "-config-alphagenome-merged-splicing",
                         "AlphaGenome merged splicing score, distilled model, Atlas precomputed (AlphaGenome Atlas v1)",
                         "AlphaGenome splice site score plus splice site usage score plus one fifth of the splice junction score, each the maximum over all positions and genes, from the distilled model with 1 Mb context.",
                         {"reported_name": "AlphaGenome merged splicing score (AG Splicing)",
                          "checkpoint": "AlphaGenome distilled model (Avsec et al.)",
                          "parameters": ("S_splicing = S_sites + S_usage + S_junctions / 5, each component the maximum over all coordinates and genes. "
                                         "Scorers (Table S1): GeneMaskSplicingScorer requested_output=SPLICE_SITES, width=None; GeneMaskSplicingScorer "
                                         "requested_output=SPLICE_SITE_USAGE, width=None (282 biosamples, 367 tracks); SpliceJunctionScorer (282 biosamples, "
                                         "367 tracks); stranded scorers merged across strands. Raw scores, no quantile transform. GRCh38, GENCODE v46. "
                                         "Genome tiled into 128 bp windows; each window scored with a 1 Mb input centred on the window, so the variant "
                                         "lies within 64 bp of the centre (not centred on the variant); reference prediction cached per window."),
                          "source_locator": "Methods 'Genome-wide inference of AlphaGenome', 'Sliding Window Approach', 'Input Features' item 1 (pages 18 to 22); Table S1 (page 69)",
                          "missing_metadata": {"version": {"reason": "unreported", "note": "API or weights release of the distilled model not printed."}}},
                         links=[{"relation": "configuration_of", "target_id": M_AG}], method_types=["foundation_model"])

    # ------------------------------------------------------------------ comparators
    def comp(key, target, name, desc, attrs, mtypes, links=()):
        attrs = dict(attrs)
        attrs.setdefault("source_locator", "Methods 'Obtaining baseline scores' (pages 26 to 27)")
        return b.entity("configuration", f"{P}-config-{key}", name, desc, attrs,
                        links=[{"relation": "configuration_of", "target_id": target}, *links], method_types=mtypes)

    need(text, "We used CADD v1.7 (GRCh38) precomputed scores.")
    cadd = comp("cadd-v1-7", M_CADD, "CADD v1.7 GRCh38, precomputed plus pipeline for missing indels (AlphaGenome Atlas v1)",
                "CADD v1.7 GRCh38 scores: genome-wide precomputed SNVs, the gnomAD v4.0 indel file, and the v1.7 Docker pipeline for remaining benchmark indels.",
                {"reported_name": "CADD v1.7", "version": "v1.7 (GRCh38)"}, ["conventional_pipeline"])
    need(text, "We scored all possible SNVs in GRCh38 with the author provided code for GPN-Star (mammalian) and GPN-Star (vertebrate)")
    gpn_v = comp("gpn-star-v", M_GPNSTAR, "GPN-Star (V), vertebrate, mutation-rate calibrated (AlphaGenome Atlas v1)",
                 "GPN-Star vertebrate model scoring all GRCh38 SNVs with the authors' code, calibrated with mutation rate; no indel scores.",
                 {"reported_name": "GPN-Star (V)", "missing_metadata": {"checkpoint_revision": {"reason": "unreported"}}}, ["foundation_model"])
    gpn_m = comp("gpn-star-m", M_GPNSTAR, "GPN-Star (M), mammalian, mutation-rate calibrated (AlphaGenome Atlas v1)",
                 "GPN-Star mammalian model scoring all GRCh38 SNVs with the authors' code, calibrated with mutation rate; no indel scores.",
                 {"reported_name": "GPN-Star (M)", "missing_metadata": {"checkpoint_revision": {"reason": "unreported"}}}, ["foundation_model"])
    cactus = comp("cactus-241way", M_PHYLOP, "Zoonomia Cactus 241-way phyloP (AlphaGenome Atlas v1)",
                  "Zoonomia 241-way Cactus alignment phyloP score at the variant position; maximum over the deleted interval for deletions.",
                  {"reported_name": "Cactus 241-way"}, ["conventional_pipeline"])
    phast = comp("phastcons-470way", M_PHASTCONS, "PhastCons 470-way (AlphaGenome Atlas v1)",
                 "PhastCons conservation probability from the 470-way vertebrate alignment; maximum over the deleted interval for deletions.",
                 {"reported_name": "Phastcons 470-way"}, ["conventional_pipeline"])
    need(text, "Allele frequency was negated so that rarer variants receive higher scores")
    gnomad_m = b.entity("method", P + "-method-gnomad-allele-frequency", "gnomAD allele frequency as a variant score",
                        "Ranks variants by negated gnomAD allele frequency so rarer variants score higher; variants absent from gnomAD get frequency 0.",
                        {"entity_level": "method", "reported_name": "gnomAD allele frequency", "version": "gnomAD v4.1 genomes",
                         "source_locator": "Methods 'Obtaining baseline scores', gnomAD allele frequency paragraph (page 27)"},
                        method_types=["conventional_pipeline"])
    gnomad = comp("gnomad-af-v4-1", gnomad_m, "gnomAD v4.1 genome allele frequency, negated (AlphaGenome Atlas v1)",
                  "Negated gnomAD v4.1 genome allele frequency, with unobserved variants set to frequency 0.",
                  {"reported_name": "gnomAD allele frequency", "version": "gnomAD v4.1 genomes"}, ["conventional_pipeline"])
    spliceai = comp("spliceai", M_SPLICEAI, "SpliceAI (AlphaGenome Atlas v1 DNM1 screen comparison)",
                    "SpliceAI splice-altering probability for each variant in the DNM1 minigene screen.",
                    {"reported_name": "SpliceAI", "source_locator": "Results 'AVI prioritization helped resolve...' paragraph 3; fig. S9E legend",
                     "missing_metadata": {"parameters": {"reason": "unreported", "note": "Scoring settings (distance, masking, model version) not printed."}}},
                    ["specialist"])
    pangolin = comp("pangolin", M_PANGOLIN, "Pangolin (AlphaGenome Atlas v1 DNM1 screen comparison)",
                    "Pangolin splice score for each variant in the DNM1 minigene screen.",
                    {"reported_name": "Pangolin", "source_locator": "Results 'AVI prioritization helped resolve...' paragraph 3; fig. S9E legend",
                     "missing_metadata": {"parameters": {"reason": "unreported", "note": "Scoring settings not printed."}}},
                    ["specialist"])

    # ------------------------------------------------------------------ ClinVar by consequence (Fig. 2A, prose values)
    need(text, "ClinVar database (June 15, 2025 release)")
    need(text, "No filter based on review status (stars) was applied.")
    d_clinvar = b.entity("dataset", P + "-data-clinvar-20250615", "ClinVar 2025-06-15 pathogenic versus benign variants, AVI evaluation set",
                         "ClinVar variants with aggregate VCV classification Pathogenic or Likely Pathogenic versus Benign or Likely Benign, excluding VUS, chrY, mitochondrial variants and indels over 10 bp, annotated with Ensembl VEP.",
                         {"version": "ClinVar release 2025-06-15", "population": ("Fig. 2B: ClinVar SNVs +151026/-997941; ClinVar indels +106995/-44767 "
                                                                                   "(positives/negatives as printed in the panel headers)"),
                          "split": ("Test set: benchmark variants at positions not overlapping any AVI training or validation variant; the same "
                                    "filter is applied to every method."),
                          "source_locator": "Methods 'ClinVar Pathogenicity Classification' (page 27); 'Overlap Filtering during Evaluation' (page 22); Fig. 2B panel headers"})
    p_clinvar = b.entity("protocol", P + "-protocol-clinvar-snv-by-consequence-auprc",
                         "ClinVar pathogenic versus benign SNVs by VEP consequence, AUPRC (AlphaGenome Atlas)",
                         "Separate ClinVar pathogenic from benign SNVs within each VEP consequence class, scored by AUPRC.",
                         {"protocol": "Within each consequence class, AUPRC of each method's score for P/LP versus B/LB ClinVar SNVs after AVI positional overlap filtering.",
                          "metric": "auprc", "metric_direction": "higher", "bootstrap_replicates": 100,
                          "uncertainty_reporting": {"printed": "Error bars indicate 95% confidence intervals from 100 bootstraps", "values_printed": False},
                          "source_locator": "Fig. 2A and legend (page 6); Methods 'ClinVar Pathogenicity Classification' (page 27)",
                          "limitations": ["Developer study; comparators run by the AVI authors.",
                                          "Positional filtering removes benchmark variants near AVI training variants for every method but comparator training data were not filtered.",
                                          "ClinVar labels include no review-status filter.",
                                          "Bar values in Fig. 2A identify methods by colour only; only values named in the text are extracted."]},
                         links=[{"relation": "uses_data", "target_id": d_clinvar}])
    strata = {"protein-altering": ("Protein altering", "+50101/-101100", 50101, 101100),
              "intronic": ("Intronic", "+3270/-353816", 3270, 353816),
              "synonymous": ("Synonymous", "+511/-421382", 511, 421382),
              "utr3": ("3' UTR", "+47/-18686", 47, 18686),
              "utr5": ("5' UTR", "+143/-18739", 143, 18739)}
    subs = {}
    for k, (label, counts, pos, neg) in strata.items():
        need(text, f"({counts})")
        subs[k] = b.entity("dataset_subset", f"{P}-subset-clinvar-snv-{k}", f"ClinVar 2025-06-15 SNVs, {label} (AlphaGenome Atlas test set)",
                           f"ClinVar SNVs annotated by VEP as {label}, after AVI positional overlap filtering.",
                           {"positive_count": pos, "test_count": pos + neg, "original_printed_counts": counts,
                            "source_locator": f"Fig. 2A panel header '{label} ({counts})' (page 6)"},
                           links=[{"relation": "used_in", "target_id": p_clinvar}])
    loc_2a = "Results 'State-of-the-art interpretable genome-wide variant prioritization with AVI' paragraph 1 (page 5), citing Fig. 2A"
    clin_vals = [  # (system id, system key, stratum, printed, sentence asserted)
        (avi_cfg, "avi", "intronic", "0.76", "intronic (AUPRC 0.76 vs. GPN-Star-V’s 0.44)"),
        (gpn_v, "gpn-star-v", "intronic", "0.44", "intronic (AUPRC 0.76 vs. GPN-Star-V’s 0.44)"),
        (avi_cfg, "avi", "synonymous", "0.57", "synonymous (0.57 vs. CADD v1.7’s 0.35)"),
        (cadd, "cadd-v1-7", "synonymous", "0.35", "synonymous (0.57 vs. CADD v1.7’s 0.35)"),
        (avi_cfg, "avi", "utr3", "0.50", "3’ UTR categories (0.50 vs. GPN-Star-M’s 0.18)"),
        (gpn_m, "gpn-star-m", "utr3", "0.18", "3’ UTR categories (0.50 vs. GPN-Star-M’s 0.18)"),
        (avi_cfg, "avi", "protein-altering", "0.90", "protein-altering variants (0.90 vs. GPN-Star-V’s 0.86)"),
        (gpn_v, "gpn-star-v", "protein-altering", "0.86", "protein-altering variants (0.90 vs. GPN-Star-V’s 0.86)"),
        (gpn_v, "gpn-star-v", "utr5", "0.27", "GPN-Star-V outperformed AVI on 5’UTR ClinVar SNVs (0.27 vs. 0.26)"),
        (avi_cfg, "avi", "utr5", "0.26", "GPN-Star-V outperformed AVI on 5’UTR ClinVar SNVs (0.27 vs. 0.26)"),
    ]
    for sys_id, key, st, printed, sentence in clin_vals:
        need(text, sentence)
        label, counts, pos, neg = strata[st]
        ev = b.evaluation(f"{P}-eval-clinvar-snv-{st}-{key}", f"{key} on ClinVar {label} SNVs (AlphaGenome Atlas Fig. 2A)", sys_id,
                          p_clinvar, subs[st],
                          {"dataset_version": "ClinVar 2025-06-15", "split": "AVI positional test filter",
                           "population": f"ClinVar {label} SNVs, {counts} (positives/negatives)", "inputs": "Precomputed or model-derived score per variant",
                           "adaptation": "None for comparators; AVI trained on gnomAD frequency labels, not ClinVar",
                           "metric_implementation": "AUPRC", "aggregation": "One AUPRC per consequence class", "budget": None},
                          f"{loc_2a}; Fig. 2A panel '{label}'",
                          missing={"comparison.budget": {"reason": "inapplicable", "note": "Pretrained scoring; no search or training budget on the benchmark."}})
        b.result(f"{P}-result-clinvar-snv-{st}-{key}-auprc", f"{key} AUPRC, ClinVar {label} SNVs", ev, printed, "auprc", "unitless",
                 f"{loc_2a}: '{sentence}'", PDF_PARSE, "Value transcribed from the prose sentence quoted in the locator; sentence asserted as an exact substring of the pdftotext -layout text (extract/build_batch.py).",
                 f"ClinVar pathogenic vs benign SNVs, {label}",
                 uncertainty_note="Fig. 2A draws 95% bootstrap intervals (100 bootstraps) without printing them.")

    # ------------------------------------------------------------------ Fig. 2B genome-wide benchmarks, prose values
    loc_2b = "Results 'State-of-the-art interpretable genome-wide variant prioritization with AVI' paragraph 1 (page 5), citing Fig. 2B"
    need(text, "TraitGym Mendelian: Validated high-penetrance pathogenic variants underlying classi- cal Mendelian disorders from OMIM matched 9:1 against gnomAD common variants.")
    s_mend = b.entity("dataset_subset", P + "-subset-traitgym-mendelian", "TraitGym Mendelian traits after AVI positional filtering (AlphaGenome Atlas)",
                      "TraitGym Mendelian OMIM non-coding variants matched 9:1 with gnomAD common variants, after removing positions overlapping AVI training or validation variants.",
                      {"positive_count": 308, "test_count": 2536, "original_printed_counts": "+308/-2228",
                       "source_locator": "Fig. 2B panel header 'Non-coding Mendelian (TraitGym) (+308/-2228)'; Methods 'TraitGym Phenotypic Association' (page 28)"},
                      links=[{"relation": "same_data_as", "target_id": D_TG_MENDELIAN}])
    s_comp = b.entity("dataset_subset", P + "-subset-traitgym-complex", "TraitGym Complex traits after AVI positional filtering (AlphaGenome Atlas)",
                      "TraitGym fine-mapped UK Biobank GWAS variants (PIP above 0.9) with matched controls (PIP below 0.01), after removing positions overlapping AVI training or validation variants.",
                      {"positive_count": 409, "test_count": 4095, "original_printed_counts": "+409/-3686",
                       "source_locator": "Fig. 2B panel header 'Fine-mapped GWAS (TraitGym) (+409/-3686)'; Methods 'TraitGym Phenotypic Association' (page 28)",
                       "limitations": ["TraitGym Complex chromosomes 2, 5, 11, 14, 17, 20, 22 and X were AVI validation data (Methods 'Data Split'); whether Fig. 2B excludes them is not stated."]},
                      links=[{"relation": "same_data_as", "target_id": D_TG_COMPLEX}])
    d_rare = b.entity("dataset", P + "-data-rare-complex-trait-variants", "Rare variants associated with complex traits, UK Biobank and All of Us meta-analysis (AlphaGenome Atlas)",
                      "Conditionally independent rare variants associated with complex traits in a UK Biobank and All of Us meta-analysis, with frequency- and sample-size-matched controls.",
                      {"population": "SNVs +2879/-2784; indels +628/-562 (fig. S7B)",
                       "source_locator": "Methods 'Complex Trait Benchmark' (pages 28 to 29); Fig. 2B panel header; fig. S7B"})
    p_mend = b.entity("protocol", P + "-protocol-traitgym-mendelian-auprc", "TraitGym Mendelian non-coding variants, AUPRC after AVI filtering (AlphaGenome Atlas)",
                      "Separate OMIM Mendelian non-coding variants from matched gnomAD common variants, scored by AUPRC.",
                      {"metric": "auprc", "metric_direction": "higher", "source_locator": "Fig. 2B; Methods 'TraitGym Phenotypic Association'"},
                      links=[{"relation": "uses_data", "target_id": s_mend}])
    p_comp = b.entity("protocol", P + "-protocol-traitgym-complex-auprc", "TraitGym fine-mapped GWAS variants, AUPRC after AVI filtering (AlphaGenome Atlas)",
                      "Separate fine-mapped causal GWAS variants from matched non-causal variants, scored by AUPRC.",
                      {"metric": "auprc", "metric_direction": "higher", "source_locator": "Fig. 2B; Methods 'TraitGym Phenotypic Association'"},
                      links=[{"relation": "uses_data", "target_id": s_comp}])
    p_rare = b.entity("protocol", P + "-protocol-rare-complex-trait-snv-auprc", "Rare complex-trait SNVs versus matched controls, AUPRC (AlphaGenome Atlas)",
                      "Separate rare SNVs associated with complex traits from frequency-matched control SNVs, scored by AUPRC.",
                      {"metric": "auprc", "metric_direction": "higher", "source_locator": "Fig. 2B 'Rare complex trait variants'; Methods 'Complex Trait Benchmark'"},
                      links=[{"relation": "uses_data", "target_id": d_rare}])
    gw_vals = [
        (avi_cfg, "avi", p_comp, s_comp, "traitgym-complex", "0.28", "TraitGym Complex, AUPRC 0.28 vs. 0.27", "TraitGym fine-mapped GWAS (Complex)", "+409/-3686"),
        (avi_cfg, "avi", p_rare, d_rare, "rare-complex-snv", "0.69", "(AUPRC 0.69 vs. GPN-Star-M’s 0.67)", "rare complex-trait SNVs", "+2879/-2784"),
        (gpn_m, "gpn-star-m", p_rare, d_rare, "rare-complex-snv", "0.67", "(AUPRC 0.69 vs. GPN-Star-M’s 0.67)", "rare complex-trait SNVs", "+2879/-2784"),
        (avi_cfg, "avi", p_mend, s_mend, "traitgym-mendelian", "0.76", "AVI ranked second to GPN-Star-M (AUPRC 0.76 vs. 0.77)", "TraitGym Mendelian non-coding", "+308/-2228"),
        (gpn_m, "gpn-star-m", p_mend, s_mend, "traitgym-mendelian", "0.77", "AVI ranked second to GPN-Star-M (AUPRC 0.76 vs. 0.77)", "TraitGym Mendelian non-coding", "+308/-2228"),
    ]
    for sys_id, key, prot, data, tag, printed, sentence, label, counts in gw_vals:
        need(text, sentence)
        ev = b.evaluation(f"{P}-eval-{tag}-{key}", f"{key} on {label} (AlphaGenome Atlas Fig. 2B)", sys_id, prot, data,
                          {"dataset_version": None, "split": "AVI positional test filter", "population": f"{label}, {counts} (positives/negatives)",
                           "inputs": "Precomputed or model-derived score per variant", "adaptation": "None",
                           "metric_implementation": "AUPRC", "aggregation": "One AUPRC over the benchmark", "budget": None},
                          f"{loc_2b}; Fig. 2B panel '{label}'",
                          missing={"comparison.budget": {"reason": "inapplicable", "note": "Pretrained scoring; no search or training budget on the benchmark."}})
        b.result(f"{P}-result-{tag}-{key}-auprc", f"{key} AUPRC, {label}", ev, printed, "auprc", "unitless",
                 f"{loc_2b}: '{sentence}'", PDF_PARSE, "Value transcribed from the prose sentence quoted in the locator; sentence asserted as an exact substring of the pdftotext -layout text.",
                 label, uncertainty_note="Fig. 2B draws 95% bootstrap intervals (100 bootstraps) without printing them.")

    # ------------------------------------------------------------------ SGE pooled AUPRC (fig. S7E, S7F legends)
    need(text, "The remaining ten studies were held out as a test evaluation of the model.")
    d_sge = b.entity("dataset", P + "-data-sge-screens", "Saturation genome editing screens of 13 genes from 14 studies (AlphaGenome Atlas)",
                     "Saturation genome editing variant effect measurements for BRCA1 (two studies), BRCA2, BAP1, RAD51C, VHL, DDX3X, RNU4-2, ATM, BARD1, PALB2, XRCC2, SFPQ and CTCF, with author thresholds defining functionally normal versus abnormal variants.",
                     {"split": ("Four studies (FINDLAY_2018_BRCA1, LEE_2025_ATM, OLVERA_LEON_2024_RAD51C, RADFORD_2023_DDX3X) used for online "
                                "validation during AVI training; the other ten held out as test, with AVI positional filtering. Variants in "
                                "'uncertain' or 'intermediate' classes removed."),
                      "source_locator": "Methods 'Saturation Genome Editing (SGE)' (pages 27 to 28)"})
    p_sge_snv = b.entity("protocol", P + "-protocol-sge-pooled-snv-auprc", "SGE held-out screens pooled, functionally abnormal versus normal SNVs, AUPRC (AlphaGenome Atlas)",
                         "Pool SNVs from the ten held-out SGE screens and separate functionally abnormal from normal variants, scored by AUPRC.",
                         {"metric": "auprc", "metric_direction": "higher", "source_locator": "fig. S7E (left) and legend (page 57)"},
                         links=[{"relation": "uses_data", "target_id": d_sge}])
    p_sge_all = b.entity("protocol", P + "-protocol-sge-pooled-all-variants-auprc", "SGE held-out screens pooled, SNVs and indels, AUPRC (AlphaGenome Atlas)",
                         "Pool SNVs and indels from the ten held-out SGE screens and separate functionally abnormal from normal variants, scored by AUPRC.",
                         {"metric": "auprc", "metric_direction": "higher", "source_locator": "fig. S7F (left) and legend (page 57)"},
                         links=[{"relation": "uses_data", "target_id": d_sge}])
    need(text, "Baseline (0.146)")
    need(text, "Baseline (0.194)")
    b.claim("sge-random-baseline", "Random-classifier AUPRC printed for the pooled SGE evaluations", p_sge_snv, "random_baseline_auprc",
            "fig. S7E legend prints 'Baseline (0.146)' for SNVs; fig. S7F legend prints 'Baseline (0.194)' for SNVs and indels.",
            "fig. S7E and S7F legends (page 57)", PDF_PARSE, "Legend strings asserted in the pdftotext -layout text.")
    sge_systems = {"AVI": (avi_cfg, "avi"), "CADD v1.7": (cadd, "cadd-v1-7"), "GPN STAR (V)": (gpn_v, "gpn-star-v"),
                   "GPN STAR (M)": (gpn_m, "gpn-star-m"), "Cactus 241-way": (cactus, "cactus-241way"),
                   "Phastcons 470-way": (phast, "phastcons-470way"), "gnomAD allele frequency": (gnomad, "gnomad-af-v4-1")}
    sge_snv = [("AVI", "0.668"), ("CADD v1.7", "0.647"), ("GPN STAR (V)", "0.425"), ("GPN STAR (M)", "0.398"),
               ("Cactus 241-way", "0.296"), ("Phastcons 470-way", "0.236"), ("gnomAD allele frequency", "0.150")]
    sge_all = [("AVI", "0.759"), ("CADD v1.7", "0.653"), ("Cactus 241-way", "0.408"), ("Phastcons 470-way", "0.316"),
               ("gnomAD allele frequency", "0.200")]
    for panel, rows, prot, scope in (("E", sge_snv, p_sge_snv, "snv"), ("F", sge_all, p_sge_all, "all-variants")):
        for label, printed in rows:
            need(text, f"{label} (AUPRC = {printed})")
            sys_id, key = sge_systems[label]
            loc = f"fig. S{7}{panel} (left) legend entry '{label} (AUPRC = {printed})' (page 57)"
            ev = b.evaluation(f"{P}-eval-sge-pooled-{scope}-{key}", f"{label} on pooled held-out SGE screens, {scope} (AlphaGenome Atlas fig. S7{panel})",
                              sys_id, prot, d_sge,
                              {"dataset_version": "Source tables and MaveDB as listed in Methods", "split": "Ten held-out SGE studies, AVI positional filter",
                               "population": "SNVs only" if scope == "snv" else "SNVs and indels; methods with indel scores only",
                               "inputs": "Precomputed or model-derived score per variant", "adaptation": "None",
                               "metric_implementation": "AUPRC, all screens pooled into one evaluation", "aggregation": "Pooled over screens", "budget": None},
                              loc, missing={"comparison.budget": {"reason": "inapplicable", "note": "Pretrained scoring."}})
            b.result(f"{P}-result-sge-pooled-{scope}-{key}-auprc", f"{label} AUPRC, pooled SGE {scope}", ev, printed, "auprc", "unitless", loc,
                     PDF_PARSE, "Legend string asserted as an exact substring of the pdftotext -layout text of the pinned PDF.",
                     "pooled held-out SGE screens, functionally abnormal vs normal, " + ("SNVs only" if scope == "snv" else "SNVs and indels"))

    # ------------------------------------------------------------------ DNM1 splicing screen (fig. S9E legend)
    need(text, "Variants are called “active” if they have both a mean alternative splicing rate of > 0.10 across all passing conditions and a minimum coherence of 0.5")
    d_dnm1 = b.entity("dataset", P + "-data-dnm1-intron-screen", "DNM1 intron saturation mutagenesis minigene splicing screen (AlphaGenome Atlas Data S1)",
                      "Minigene reporter screen of mutagenised variants in the 265 nt upstream of DNM1 exon 10a, assayed in five cell line and promoter combinations, with variants called active when they shift 3' splice site use.",
                      {"assay": "Barcoded minigene splicing reporter, amplicon RNA-seq, three biological replicates; HEK293, KELLY, T47D, A172, DAOY or GAMG cells (five passing cell line and promoter combinations)",
                       "label_semantics": ("Active: mean alternative 3' splice site rate above 0.10 across passing conditions and dominant alternative "
                                           "site coherence at least 0.5. 12 intronic variants produced in-frame exon extensions."),
                       "source_locator": "Methods 'Experimental splicing screen of DNM1 intron' (pages 43 to 44); Results paragraph on DNM1 (page 8)",
                       "missing_metadata": {"variant_count": {"reason": "unreported", "note": "Numbers of active and inactive variants scored in fig. S9E not printed in the text."}}},
                      contexts=("research",))
    p_dnm1 = b.entity("protocol", P + "-protocol-dnm1-active-variant-ap", "DNM1 minigene screen, active versus inactive variants, average precision (AlphaGenome Atlas)",
                      "Separate variants that the DNM1 minigene screen calls active from inactive variants, scored by average precision.",
                      {"metric": "average-precision", "metric_direction": "higher",
                       "metric_definition": "Legend prints AP; the Results text calls the same values AUPRC.",
                       "source_locator": "fig. S9E and legend (pages 60 to 61); Results page 8"},
                      links=[{"relation": "uses_data", "target_id": d_dnm1}])
    dnm1_rows = [("AVI PHRED", "0.708", avi_cfg, "avi"), ("AG Splicing", "0.943", ag_splice, "alphagenome-merged-splicing"),
                 ("AVI Splicing SHAP attribution", "0.943", avi_shap, "avi-splicing-shap"), ("SpliceAI", "0.940", spliceai, "spliceai"),
                 ("Pangolin", "0.939", pangolin, "pangolin"), ("GPN-Star (M)", "0.260", gpn_m, "gpn-star-m"),
                 ("GPN-Star (V)", "0.348", gpn_v, "gpn-star-v"), ("CADD PHRED", "0.289", cadd, "cadd-v1-7")]
    need(text, "SpliceAI (41) and Pangolin (42) also performed well at this task (AUPRC: 0.940 and 0.939, respectively)")
    need(text, "both CADD v1.7 (AUPRC: 0.289) and conservation based methods (e.g. GPN-Star (V) with AUPRC: 0.348)")
    for label, printed, sys_id, key in dnm1_rows:
        need(text, f"{label} (AP={printed})")
        loc = f"fig. S9E legend entry '{label} (AP={printed})' (page 60)"
        ev = b.evaluation(f"{P}-eval-dnm1-{key}", f"{label} on the DNM1 minigene splicing screen (AlphaGenome Atlas fig. S9E)", sys_id, p_dnm1, d_dnm1,
                          {"dataset_version": "Data S1 (not retrieved)", "split": "None; prospective experimental screen",
                           "population": "Screened variants in the 265 nt upstream of DNM1 exon 10a passing UMI and replicate filters",
                           "inputs": "Precomputed or model-derived score per variant", "adaptation": "None",
                           "metric_implementation": "Average precision (legend 'AP'; text 'AUPRC')", "aggregation": "One value over the screen", "budget": None},
                          loc, missing={"comparison.budget": {"reason": "inapplicable", "note": "Pretrained scoring."}})
        b.result(f"{P}-result-dnm1-{key}-ap", f"{label} AP, DNM1 splicing screen", ev, printed, "average-precision", "unitless", loc,
                 PDF_PARSE, "Legend string asserted as an exact substring of the pdftotext -layout text; values also asserted against the Results prose where it names them.",
                 "DNM1 minigene screen, active vs inactive variants")

    # ------------------------------------------------------------------ GREGoR retrospective ranking
    need(text, "AVI ranked the known likely pathogenic and pathogenic variants among all variants in each patient more highly than CADD v1.7, with a recall of 29.5% compared to CADD v1.7’s 12.5% when considering the top 50 variants ranked by either method")
    need(text, "the recall at top 50 variants increased to 74.3% and 61% for AVI and CADD v1.7, respectively")
    d_greg = b.entity("dataset", P + "-data-gregor-solved-cases", "GREGoR solved rare disease cases, likely pathogenic and pathogenic variants (AlphaGenome Atlas)",
                      "Likely pathogenic and pathogenic SNVs and indels from solved GREGoR Consortium rare disease cases, each ranked against all other variants in the same patient.",
                      {"population": "112 likely pathogenic variants from solved cases (Fig. 3A); 105 after an allele frequency cutoff of 0.001 (fig. S9A)",
                       "access": "GREGoR Consortium controlled-access data",
                       "source_locator": "Fig. 3A legend (page 9); fig. S9A legend (page 60); Methods 'GREGoR retrospective' (page 29)"},
                      contexts=("clinical_research",))
    p_greg = b.entity("protocol", P + "-protocol-gregor-recall-top50", "GREGoR solved cases, recall of causal variants in the top 50 per patient (AlphaGenome Atlas)",
                      "Rank all variants in each solved patient and count the fraction of known likely pathogenic or pathogenic variants within the top 50.",
                      {"metric": "recall", "metric_direction": "higher", "unit": "percent", "source_locator": "Fig. 3A and fig. S9A; Results page 7"},
                      links=[{"relation": "uses_data", "target_id": d_greg}])
    loc_g = "Results 'AVI prioritization helped resolve a rare disease case...' paragraph 1 (page 7)"
    for key, sys_id, printed, scope, pop in (("avi", avi_cfg, "29.5%", "all-variants", "112 causal variants, all patient variants"),
                                             ("cadd-v1-7", cadd, "12.5%", "all-variants", "112 causal variants, all patient variants"),
                                             ("avi", avi_cfg, "74.3%", "af-filtered", "105 causal variants, background filtered at gnomAD AF 0.001"),
                                             ("cadd-v1-7", cadd, "61%", "af-filtered", "105 causal variants, background filtered at gnomAD AF 0.001")):
        ev_id = f"{P}-eval-gregor-{scope}-{key}"
        if ev_id not in b.ids:
            b.evaluation(ev_id, f"{key} on GREGoR solved cases, {scope} (AlphaGenome Atlas)", sys_id, p_greg, d_greg,
                         {"dataset_version": None, "split": "Retrospective; solved cases", "population": pop,
                          "inputs": "SNVs and indels from patient genomes", "adaptation": "None",
                          "metric_implementation": "Cumulative recall at rank threshold K = 50", "aggregation": "Pooled over causal variants", "budget": None},
                         f"{loc_g}; Fig. 3A" if scope == "all-variants" else f"{loc_g}; fig. S9A",
                         missing={"comparison.budget": {"reason": "inapplicable", "note": "Pretrained scoring."}})
        b.result(f"{P}-result-gregor-{scope}-{key}-recall-top50", f"{key} recall in top 50, GREGoR {scope}", ev_id, printed, "recall", "percent",
                 loc_g, PDF_PARSE, "Value transcribed from the prose sentence; sentence asserted as an exact substring of the pdftotext -layout text.",
                 "known P/LP variants ranked within the top 50 of each patient's variants; " + pop)

    # ------------------------------------------------------------------ Table S2 ablations
    t = layout[layout.index("Table S2 | Performance across benchmark evaluations"):layout.index("Table S3 | Oligonucleotide")]
    need(flat(t), "Absolute AUPRC values are shown for the AVI baseline model, while subsequent rows display the percentage difference relative to this baseline.")
    hdr = re.search(r"Ablation\s+ClinVar\s+ncVar\s+SGE\s+Complex\s+Mendelian", t)
    assert hdr, "Table S2 header"
    cols = ["clinvar", "ncvar", "sge", "traitgym-complex", "traitgym-mendelian"]
    col_labels = ["ClinVar", "ncVar", "SGE", "TraitGym Complex", "TraitGym Mendelian"]
    expected = [  # (section, printed row label, key, description)
        ("Baseline", "AVI Model", "baseline", None),
        ("Features Set to Zero", "+ No Indel Type", "zero-indel-type", "Frozen AVI ensemble with the two indel-type features set to zero at inference."),
        ("Features Set to Zero", "No AlphaMissense Indel Features", "zero-alphamissense-indel", "Frozen AVI ensemble without the inference-time AlphaMissense imputation for indels."),
        ("Features Set to Zero", "+ No Indel Type", "zero-alphamissense-indel-and-indel-type", "Frozen AVI ensemble without AlphaMissense indel imputation and with indel-type features set to zero."),
        ("Retrained", "AlphaGenome", "retrained-no-alphagenome", "AVI ensemble retrained with the ten AlphaGenome features set to zero."),
        ("Retrained", "Splicing Removed Only", "retrained-no-splicing", "AVI ensemble retrained with only the AlphaGenome merged splicing feature set to zero."),
        ("Retrained", "Protein", "retrained-no-protein", "AVI ensemble retrained with AlphaMissense and the VEP consequence features set to zero."),
        ("Retrained", "AlphaMissense", "retrained-no-alphamissense", "AVI ensemble retrained with the AlphaMissense feature set to zero."),
        ("Retrained", "Consequence", "retrained-no-consequence", "AVI ensemble retrained with the three VEP loss-of-function features set to zero."),
        ("Retrained", "Conservation", "retrained-no-conservation", "AVI ensemble retrained with the PhastCons and Cactus features set to zero."),
        ("Retrained", "Cactus", "retrained-no-cactus", "AVI ensemble retrained with the Cactus 241-way feature set to zero."),
        ("Retrained", "PhastCons", "retrained-no-phastcons", "AVI ensemble retrained with the PhastCons 470-way feature set to zero."),
        ("Retrained", "Indel Type", "retrained-no-indel-type", "AVI ensemble retrained with the two indel-type features set to zero."),
        ("Retrained", "All except AlphaGenome", "retrained-all-except-alphagenome", "AVI ensemble retrained under the ablation the table labels 'All except AlphaGenome'."),
    ]
    rows = []
    for line in t[hdr.end():].splitlines():
        m = re.match(r"^\s*(Baseline|Features Set to Zero|Retrained)?\s*(.+?)\s{2,}(-?\d+\.\d+%?)\s+(-?\d+\.\d+%?)\s+(-?\d+\.\d+%?)\s+(-?\d+\.\d+%?)\s+(-?\d+\.\d+%?)\s*$", line)
        if m:
            rows.append((m.group(2).strip(), list(m.group(3, 4, 5, 6, 7))))
    assert [r[0] for r in rows] == [e[1] for e in expected], [r[0] for r in rows]
    protocols, datasets = {}, {}
    d_ncvar = b.entity("dataset", P + "-data-ncvardb", "ncVarDB non-coding pathogenic and benign variants (as used in AlphaGenome Atlas)",
                       "Curated non-coding variants: 721 high-confidence pathogenic or functionally disruptive variants and 7,228 common benign variants.",
                       {"positives": 721, "negatives": 7228,
                        "population": "fig. S7A after AVI filtering: SNVs +577/-4490, indels +18/-133",
                        "source_locator": "Methods 'ncVarDB Benchmark' (page 29); fig. S7A panel header"})
    datasets = {"clinvar": d_clinvar, "ncvar": d_ncvar, "sge": d_sge, "traitgym-complex": s_comp, "traitgym-mendelian": s_mend}
    for c, cl in zip(cols, col_labels):
        protocols[c] = b.entity("protocol", f"{P}-protocol-table-s2-{c}", f"AVI feature ablation, {cl} column, AUPRC (AlphaGenome Atlas Table S2)",
                                f"Score the {cl} evaluation set with the full AVI model and with each ablated AVI model, reporting the full model's AUPRC and each ablation's percentage difference from it.",
                                {"metric": "auprc", "metric_direction": "higher",
                                 "source_locator": "Table S2 and caption (page 70); Methods 'Feature Ablations' (page 27)",
                                 "limitations": ["Table S2 does not say which variants (SNVs, indels, test or validation split) each column uses; its AVI values differ from Fig. 2 and fig. S7 for ClinVar and SGE.",
                                                 "The caption says the best result per column is bolded; bolding is not captured in the text layer and is not recorded.",
                                                 "No uncertainty is printed."]},
                                links=[{"relation": "uses_data", "target_id": datasets[c]}])
    for (section, label, key, desc), (row_label, vals) in zip(expected, rows):
        if key == "baseline":
            sys_id = avi_cfg
        else:
            sys_id = b.entity("configuration", f"{P}-config-avi-ablation-{key}", f"AVI ablation '{label}' ({section}, AlphaGenome Atlas Table S2)", desc,
                              {"reported_name": label, "parameters": f"Table S2 section '{section}', row '{label}'. " +
                               ("Inference-time zeroing on the frozen AVI ensemble; '+' applies 'No Indel Type' to the row above." if section == "Features Set to Zero"
                                else "Ensemble of six retrained models with the same hyperparameters and checkpoint selection as AVI."),
                               "source_locator": "Table S2 and caption (page 70); Methods 'Feature Ablations' (page 27)",
                               **({"model_identity_note": ("The caption defines the Protein and Conservation groups but not 'All except AlphaGenome'. "
                                                           "It may mean a model keeping only the AlphaGenome features; the paper does not say.")}
                                  if key == "retrained-all-except-alphagenome" else {})},
                              links=[{"relation": "configuration_of", "target_id": avi}], method_types=["supervised_machine_learning"])
        for c, cl, printed in zip(cols, col_labels, vals):
            loc = f"Table S2 (page 70), section '{section}', row '{label}', column '{cl}'"
            ev = b.evaluation(f"{P}-eval-table-s2-{key}-{c}", f"AVI {label} ({section}) on {cl} (AlphaGenome Atlas Table S2)", sys_id, protocols[c], datasets[c],
                              {"dataset_version": None, "split": None, "population": None, "inputs": "AVI feature vector with the stated features zeroed",
                               "adaptation": "Retrained" if section == "Retrained" else "None (frozen AVI ensemble)",
                               "metric_implementation": "AUPRC" if key == "baseline" else "Percentage difference in AUPRC relative to the AVI baseline row",
                               "aggregation": None, "budget": None}, loc,
                              missing={"comparison.budget": {"reason": "inapplicable", "note": "No search budget on the benchmark."}})
            if key == "baseline":
                b.result(f"{P}-result-table-s2-{key}-{c}-auprc", f"AVI AUPRC, {cl} (Table S2 baseline)", ev, printed, "auprc", "unitless", loc,
                         TABLE_PARSE, "Parsed from pdftotext -layout text of Table S2 with every row label and the column header asserted (extract/build_batch.py).",
                         f"AVI baseline row, {cl} column")
            else:
                assert printed.endswith("%"), printed
                b.result(f"{P}-result-table-s2-{key}-{c}-auprc-relative-difference", f"AVI ablation '{label}' AUPRC difference, {cl} (Table S2)", ev,
                         printed, "auprc-relative-difference", "percent", loc, TABLE_PARSE,
                         "Parsed from pdftotext -layout text of Table S2 with every row label and the column header asserted (extract/build_batch.py).",
                         f"relative to the AVI baseline row ({section}, '{label}'), {cl} column")

    # ------------------------------------------------------------------ claims on scoring setup and gaps
    need(text, "we re-ran the AlphaGenome paper evaluations with variants placed at their windowed positions rather than centered on the interval, and observed no statistically significant differences in any evaluation metric.")
    b.claim("alphagenome-window-position", "AlphaGenome Atlas: variant offset from the input centre", ag_splice, "scoring_setup",
            ("Atlas scores use a 1 Mb input centred on each 128 bp window, so variants sit up to 64 bp from the centre. The authors re-ran the "
             "AlphaGenome paper evaluations with variants at their windowed positions and report no statistically significant difference in any evaluation metric."),
            "Methods 'Sliding Window Approach' and 'Reference Prediction Caching' (pages 18 to 19)", PDF_PARSE, "Sentences asserted in the pdftotext -layout text.",
            limitations=["The re-run metrics are not printed."])
    need(text, "To eliminate these artifacts, we perform intermediate activation stitching on the base-resolution representation of the model before evaluating the prediction heads")
    b.claim("alphagenome-indel-shift-augmentation", "AlphaGenome Atlas: indel scoring with shift augmentation", M_AG, "indel_scoring",
            ("Atlas scores indels with three forward passes: the reference-aligned pass, a pass shifted to align bases after the variant, and the unstitched "
             "allele; the base-resolution embeddings are stitched before the heads. Coarse 128 bp and 2,048 bp bins are shifted from the final bin the indel ends in."),
            "Methods 'Indel Scoring', 'Indel shift augmentation', 'Base Resolution', 'Coarse Resolution' (pages 19 to 20)", PDF_PARSE, "Sentences asserted in the pdftotext -layout text.")
    need(text, "Because the same training-set exclusion was not performed for external comparator models, any baseline overlap with benchmark sets presents a conservative bias against AVI.")
    b.claim("developer-evaluation", "AlphaGenome Atlas evaluations are developer-run", avi, "evaluation_actor",
            ("All AVI and comparator evaluations were run by the AlphaGenome Atlas authors, led by Google DeepMind, which also develops AlphaGenome and "
             "AlphaMissense. Benchmark variants overlapping AVI training or validation positions are removed for all methods; comparator training sets were not filtered."),
            "Author list and affiliations (page 1); Methods 'Overlap Filtering during Evaluation' (page 22)", PDF_PARSE, "Statements asserted in the pdftotext -layout text.")
    b.claim("figures-not-extracted", "AlphaGenome Atlas values not extracted", S, "extraction_gap",
            ("Not extracted: Fig. 2A and 2B bar labels other than those the text names (bars sorted by value and identified only by colour, "
             "so ClinVar SNV and indel overall AUPRCs and most comparator values are unattributed); fig. S7A ClinVar UTR, intronic and ncVar SNV-plus-indel bars "
             "(same problem); Fig. 2D and fig. S7D per-gene Spearman correlations (no printed values); fig. S7E and S7F precision at 90% recall (no printed values); "
             "Fig. 3A curve labels at K other than 50 (attributed by colour); TraitGym Complex comparator value 0.27 (the text does not name the method); "
             "all 95% bootstrap confidence intervals (drawn, not printed)."),
            "Fig. 2 (page 6), Fig. 3A (page 9), fig. S7 (page 57)", ["transcription"], "Scope decision recorded by the extractor.")


def main(art, out):
    path = os.path.join(art, PDF)
    assert sha256(path) == PDF_SHA, "artifact hash mismatch"
    layout = subprocess.run(["pdftotext", "-layout", path, "-"], check=True, capture_output=True, text=True).stdout
    text = flat(layout)
    b = Batch()
    build(b, text, layout)
    os.makedirs(out, exist_ok=True)
    recs = sorted(b.records, key=lambda r: r["id"])
    with open(os.path.join(out, "batch.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    with open(os.path.join(out, "claims.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for row in sorted(b.rows):
            w.writerow(row)
    counts = {}
    for r in recs:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main(*sys.argv[1:3])
