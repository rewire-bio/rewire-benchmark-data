"""Build the gfm-guides-20261014-gpnmsa batch from the pinned artifacts.

Usage (python3 -I):
  build_gpnmsa.py <v2.pdf> <v2.txt from `pdftotext -layout v2.pdf v2.txt`> <README.md> <gpn-msa.md> <batch-dir>

Asserts the SHA-256 of every input, parses Supplementary Table 4 from the PDF text layer with its
row and column labels asserted, and checks that the two DMS TADBP values are present verbatim.
"""
import csv, hashlib, json, re, sys

PDF, TXT, README, DOC, OUT = sys.argv[1:6]

PDF_SHA = "10411077df1ae59614f9a9a9f85384103d54127ba67a9b3c469a4a2d6c33cee4"
README_SHA = "0312fb9646aef630a30cd3039337b31a48f4345f4dd1cdd71edcc483afd8b9d0"
DOC_SHA = "8076d5e5ced9447904acc6fce3352030299e8701220f738b047fcefd0a1edaee"
PDF_URL = "https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf"
COMMIT = "dc5fd287599f2955a79d010bca0e0f7f8178c67e"
README_URL = f"https://raw.githubusercontent.com/songlab-cal/gpn/{COMMIT}/README.md"
DOC_URL = f"https://raw.githubusercontent.com/songlab-cal/gpn/{COMMIT}/docs/models/gpn-msa.md"
DATE = "2026-10-14"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


assert sha(PDF) == PDF_SHA, "PDF hash mismatch"
assert sha(README) == README_SHA, "README hash mismatch"
assert sha(DOC) == DOC_SHA, "gpn-msa.md hash mismatch"
text = open(TXT, encoding="utf-8").read()

P = "gfm-guides-20261014-gpnmsa"
S_PDF = f"{P}-source-biorxiv-v2"
S_README = f"{P}-source-gpn-readme"
S_DOC = f"{P}-source-gpn-msa-doc"
ESM1B_MODEL = "uc20260930-model-esm-1b"
AREAS = {"areas": ["dna-genomes"], "contexts": ["research"]}
EXTRACTOR_NOTE = ("Extraction agent for rewire-benchmark-data issue #129 (GPN-MSA and ESM-1b guide evidence); "
                  "extraction only, not a review. Pending an independent review-evidence pass.")

records, claims_rows = [], []


def review(method, note, artifact=PDF_SHA, url=PDF_URL, method_note=None):
    r = {"method": method, "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE, "date": DATE,
         "artifact_sha256": artifact, "retrieval_url": url, "note": note}
    if method_note:
        r["method_note"] = method_note
    return r


def add(rec):
    records.append(rec)
    return rec["id"]


# ---------------------------------------------------------------- sources
add({"id": S_PDF, "kind": "source",
     "name": "GPN-MSA: an alignment-based DNA language model for genome-wide variant effect prediction (bioRxiv v2)",
     "description": "Preprint of the GPN-MSA paper (Benegas, Albors, Aw, Ye and Song), version 2, retrieved as PDF.",
     "status": "needs_review", "facets": dict(AREAS), "source_ids": [], "links": [],
     "attributes": {
         "url": "https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2",
         "artifact_url": PDF_URL,
         "doi": "10.1101/2023.10.10.561776",
         "version": "bioRxiv v2, posted 2024-04-06",
         "retrieved_at": "2026-10-14T12:02:16Z",
         "artifact_sha256": PDF_SHA,
         "publication_status": "preprint",
         "licence": "CC BY-NC-ND 4.0",
         "media_type": "application/pdf",
         "venue": "bioRxiv",
         "year": 2024,
         "limitations": [
             "Preprint. The peer-reviewed version is Benegas et al., Nature Biotechnology 43, 1960-1965 (2025), doi:10.1038/s41587-024-02511-w, which is not open access; its Extended Data Table 1 (Ablation study) is published only as an image and was not read, so the printed values here may differ from the journal version.",
             "The issue named bioRxiv 2023.10.10.562811; that DOI does not resolve. bioRxiv and Crossref give 10.1101/2023.10.10.561776 for this preprint, and the bioRxiv API lists the journal DOI 10.1038/s41587-024-02511-w as its published version.",
             "The main comparisons with CADD, phyloP, ESM-1b, Nucleotide Transformer and HyenaDNA on ClinVar, COSMIC, OMIM and gnomAD (Figure 2c-f, Supplementary Figures 3-5) are printed only as figures and were not extracted.",
             "Supplementary Table 4 caption says ClinVar, COSMIC, OMIM and gnomAD use 'same setting as Figure 2a', '2b', '2c' and '2d', but in v2 those settings are Figure 2c, 2d, 2e and 2f (Figure 2 caption and Results). The settings were taken from the Methods 'Main VEP metrics' and the caption's own description.",
             "Licence CC BY-NC-ND 4.0; no archived copy is kept in the batch folder.",
         ],
         "source_locator": "Supplementary Table 4 (PDF page 23); Results paragraph on DMS (PDF page 6); Methods 'Ablation Study', 'VEP data sources', 'Main VEP metrics', 'Additional VEP metrics', 'VEP scores'",
         "review": review(["source-hash-verification"], "Retrieved once and hashed; not yet re-retrieved by a reviewer."),
     }})
for sid, url, sh, name, loc in [
    (S_README, README_URL, README_SHA, "songlab-cal/gpn README at commit dc5fd287", "README.md, model table and citation section"),
    (S_DOC, DOC_URL, DOC_SHA, "songlab-cal/gpn docs/models/gpn-msa.md at commit dc5fd287", "docs/models/gpn-msa.md, all sections"),
]:
    add({"id": sid, "kind": "source", "name": name,
         "description": "Official GPN repository file by the GPN-MSA authors, pinned to a commit.",
         "status": "needs_review", "facets": dict(AREAS), "source_ids": [], "links": [],
         "attributes": {
             "url": "https://github.com/songlab-cal/gpn",
             "artifact_url": url,
             "version": f"git commit {COMMIT} (main, committed 2026-09-26)",
             "retrieved_at": "2026-10-14T12:05:43Z" if sid == S_README else "2026-10-14T12:06:06Z",
             "artifact_sha256": sh,
             "publication_status": "official_project_source",
             "licence": "MIT",
             "media_type": "text/markdown",
             "source_locator": loc,
             "review": review(["source-hash-verification"], "Retrieved once and hashed; not yet re-retrieved by a reviewer.", sh, url),
         }})

# ---------------------------------------------------------------- model
MODEL = add({"id": f"{P}-model-gpn-msa", "kind": "model", "name": "GPN-MSA",
             "description": "DNA language model trained on a human-centred multispecies whole-genome alignment; scores a variant as the log-likelihood ratio of the alternate and reference allele.",
             "status": "needs_review",
             "facets": {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["foundation_model"]},
             "source_ids": [S_PDF, S_README, S_DOC], "links": [],
             "attributes": {
                 "reported_name": "GPN-MSA",
                 "entity_level": "family",
                 "identity_scope": "Family record for the GPN-MSA model described by Benegas et al.; the published human checkpoint is songlab/gpn-msa-sapiens. Ablation and evaluation variants are configurations.",
                 "training_data": "Human reference genome with a multispecies whole-genome alignment of vertebrates (89 non-human species in the default model); prepared human training regions are published as songlab/gpn-msa-sapiens-dataset",
                 "access": "Published checkpoint songlab/gpn-msa-sapiens on Hugging Face; inference with the gpn package ('gpn msa {vep,logits,embedding}'). The repository marks GPN-MSA as deprecated in favour of GPN-Star and no longer maintains training.",
                 "licence": "Code: MIT (songlab-cal/gpn). Checkpoint licence not checked.",
                 "source_locator": "gpn-msa.md 'Quick start' and 'Published assets'; README model table; preprint v2 Figure 2a caption ('89 non-human species') and Methods",
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}},
             }})
add({"id": f"{P}-claim-gpn-msa-maintenance-status", "kind": "claim",
     "name": "maintenance_status: GPN-MSA", "description": "Descriptive fact transcribed from the pinned source.",
     "status": "needs_review", "facets": {}, "source_ids": [S_DOC, S_README],
     "links": [{"relation": "subject", "target_id": MODEL}],
     "attributes": {
         "field": "maintenance_status",
         "value": "The official repository says GPN-MSA is deprecated in favour of GPN-Star: the maintained package supports inference from the published model (songlab/gpn-msa-sapiens) but not GPN-MSA training. It requires aligned genomes for training and inference.",
         "source_locator": "docs/models/gpn-msa.md paragraph 1 and 'Model and evaluations'; README model table row 'GPN-MSA'",
         "review": review(["transcription"], "Transcribed from the pinned markdown files.", DOC_SHA, DOC_URL),
     }})
claims_rows.append([f"{P}-claim-gpn-msa-maintenance-status", S_DOC, "docs/models/gpn-msa.md paragraph 1; README model table row 'GPN-MSA'", "deprecated in favor of GPN-Star", "claim"])

# ---------------------------------------------------------------- benchmark, datasets, protocols
BENCH = add({"id": f"{P}-benchmark-gpn-msa-vep", "kind": "benchmark",
             "name": "GPN-MSA variant effect prediction evaluation (Benegas et al.)",
             "description": "The authors' variant effect benchmarks in the GPN-MSA paper: ClinVar, COSMIC and OMIM against gnomAD common variants, gnomAD rare versus common enrichment, ProteinGym DMS and DepMap.",
             "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF], "links": [],
             "attributes": {
                 "entity_level": "suite",
                 "version": "bioRxiv v2 (2024-04-06)",
                 "task": "Genome-wide variant effect (deleteriousness) prediction",
                 "scope_note": "Only Supplementary Table 4 (ablation study; ClinVar, COSMIC and OMIM columns) and the printed DMS TADBP AUROCs are extracted. The labelled datasets are published as songlab/clinvar, songlab/cosmic, songlab/omim and songlab/gnomad on Hugging Face (gpn-msa.md), not retrieved here.",
                 "source_locator": "Methods 'VEP data sources', 'Main VEP metrics' and 'Additional VEP metrics'",
             }})

D_CLINVAR = add({"id": f"{P}-data-clinvar-vs-gnomad-common-missense", "kind": "dataset",
                 "name": "ClinVar Pathogenic vs gnomAD common missense variants (GPN-MSA paper)",
                 "description": "ClinVar 'Pathogenic' missense variants as positives and gnomAD common (MAF > 5%) missense variants as controls.",
                 "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF, S_DOC], "links": [],
                 "attributes": {
                     "version": "ClinVar release 20230730; gnomAD v3.1.2 (allele number at least 25,000 and official QC flags)",
                     "split": "Whole labelled set; no training on labels (zero-shot scores)",
                     "population": "ClinVar 'Pathogenic' missense versus gnomAD missense variants with MAF > 5%",
                     "source_locator": "Methods 'VEP data sources' (ClinVar, gnomAD) and 'Main VEP metrics' (ClinVar)",
                     "missing_metadata": {"denominator": {"reason": "unreported", "note": "Variant counts are not printed in the text or Supplementary Table 4"}},
                 }})
D_COSMIC = add({"id": f"{P}-data-cosmic-frequent-vs-gnomad-common-missense", "kind": "dataset",
                "name": "COSMIC frequent vs gnomAD common missense variants (GPN-MSA paper)",
                "description": "COSMIC somatic missense mutations with frequency above 0.1% as positives and gnomAD common missense variants as controls.",
                "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF], "links": [],
                "attributes": {
                    "version": "COSMIC Cosmic_MutantCensus v98 GRCh38 (frequency over whole-genome or whole-exome samples); gnomAD v3.1.2",
                    "split": "Whole labelled set; no training on labels (zero-shot scores)",
                    "population": "COSMIC missense mutations with frequency > 0.1% versus gnomAD missense variants with MAF > 5%",
                    "source_locator": "Methods 'VEP data sources' (COSMIC, gnomAD) and 'Main VEP metrics' (COSMIC)",
                    "missing_metadata": {"denominator": {"reason": "unreported", "note": "Variant counts are not printed in the text or Supplementary Table 4"}},
                }})
D_OMIM = add({"id": f"{P}-data-omim-vs-gnomad-common-regulatory", "kind": "dataset",
              "name": "OMIM pathogenic vs gnomAD common regulatory variants (GPN-MSA paper)",
              "description": "Curated OMIM pathogenic regulatory variants as positives and matched gnomAD common variants as controls (promoter with upstream-of-gene, enhancer with intergenic).",
              "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF], "links": [],
              "attributes": {
                  "version": "OMIM curated pathogenic regulatory variant set (download date not printed); gnomAD v3.1.2",
                  "split": "Whole labelled set; no training on labels (zero-shot scores)",
                  "population": "OMIM pathogenic regulatory variants versus gnomAD common (MAF > 5%) variants matched by category; 'all' is the union of the category matches",
                  "source_locator": "Methods 'VEP data sources' (OMIM, gnomAD) and 'Main VEP metrics' (OMIM)",
                  "missing_metadata": {"denominator": {"reason": "unreported", "note": "Variant counts are not printed in the text or Supplementary Table 4"}},
              }})
D_TADBP = add({"id": f"{P}-data-proteingym-dms-tadbp-bolognesi2019", "kind": "dataset",
               "name": "ProteinGym v0.1 DMS TADBP_HUMAN Bolognesi 2019, binarised (GPN-MSA paper)",
               "description": "TDP-43 (TADBP) deep mutational scan from ProteinGym v0.1, binarised with a cutoff of 0.125 on the absolute value of relative toxicity.",
               "status": "needs_review", "facets": {"areas": ["dna-genomes", "protein-function"], "contexts": ["research"]},
               "source_ids": [S_PDF], "links": [],
               "attributes": {
                   "version": "ProteinGym v0.1, assay 'DMS TADBP HUMAN Bolognesi 2019'",
                   "split": "Whole assay; no training on labels (zero-shot scores)",
                   "population": "Amino-acid substitutions in the TADBP assay; for genomic predictors the most deleterious score among the SNVs causing each substitution was used",
                   "source_locator": "Supplementary Table 3; Methods 'VEP data sources' (DMS) and 'Additional VEP metrics' (DMS)",
                   "missing_metadata": {"denominator": {"reason": "unreported"}},
               }})

PROTO = {}
for key, data, name, metric, desc, loc in [
    ("clinvar", D_CLINVAR, "ClinVar Pathogenic vs gnomAD common missense, AUROC (GPN-MSA Supplementary Table 4)", "auroc",
     "AUROC of zero-shot variant scores for ClinVar 'Pathogenic' versus gnomAD common missense variants.",
     "Methods 'Main VEP metrics' (ClinVar); Supplementary Table 4 column 'ClinVar'"),
    ("cosmic", D_COSMIC, "COSMIC frequent vs gnomAD common missense, AUPRC (GPN-MSA Supplementary Table 4)", "auprc",
     "AUPRC of zero-shot variant scores for COSMIC frequent (> 0.1%) versus gnomAD common missense variants.",
     "Methods 'Main VEP metrics' (COSMIC); Supplementary Table 4 column 'COSMIC'"),
    ("omim", D_OMIM, "OMIM pathogenic vs gnomAD common regulatory variants, AUPRC (GPN-MSA Supplementary Table 4)", "auprc",
     "AUPRC of zero-shot variant scores for OMIM pathogenic regulatory variants versus matched gnomAD common variants.",
     "Methods 'Main VEP metrics' (OMIM); Supplementary Table 4 column 'OMIM'"),
]:
    PROTO[key] = add({"id": f"{P}-protocol-ablation-{key}-{metric}", "kind": "protocol", "name": name,
                      "description": desc, "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF],
                      "links": [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data}],
                      "attributes": {
                          "protocol": "Each model or score is applied zero-shot (no training on these labels). GPN-MSA scores are the log-likelihood ratio of alternate versus reference allele averaged over both strands. For each ablation setting three replicate models with different seeds were trained where applicable; the table prints the mean and the maximum over seeds.",
                          "version": "bioRxiv v2 Supplementary Table 4",
                          "metric": metric, "metric_direction": "higher", "unit": "unitless",
                          "limitations": [
                              "Benchmark built and run by the GPN-MSA authors (author-reported).",
                              "Controls are gnomAD common variants rather than ClinVar benign variants; the authors report that with ClinVar benign controls GPN-MSA is slightly behind CADD and ESM-1b (Supplementary Figure 4, figure only).",
                              "Variant counts are not printed.",
                          ],
                          "source_locator": loc,
                      }})
P_TADBP = add({"id": f"{P}-protocol-dms-tadbp-auroc", "kind": "protocol",
               "name": "ProteinGym DMS TADBP binary classification, AUROC (GPN-MSA paper)",
               "description": "AUROC of zero-shot scores against TADBP DMS labels binarised at 0.125 absolute relative toxicity.",
               "status": "needs_review", "facets": {"areas": ["dna-genomes", "protein-function"], "contexts": ["research"]},
               "source_ids": [S_PDF],
               "links": [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": D_TADBP}],
               "attributes": {
                   "protocol": "Labels: absolute value of relative toxicity binarised at 0.125 (TADBP only; other assays use the ProteinGym protein-specific cutoff). Genomic predictors take the most deleterious score among SNVs causing each substitution; ESM-1b uses precomputed log-likelihood ratios in protein coordinates, minimum over isoforms.",
                   "version": "bioRxiv v2",
                   "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
                   "limitations": ["Single assay, quoted in the Results text as an example where GPN-MSA beats ESM-1b; the 31-assay summary is figure-only (Supplementary Figure 5).",
                                   "Values printed to two decimals."],
                   "source_locator": "Results paragraph beginning 'We also evaluate on deep mutational scanning' (PDF page 6); Methods 'Additional VEP metrics' (DMS) and 'VEP scores'",
               }})

# ---------------------------------------------------------------- Supplementary Table 4
ROWS = [
    # printed label, slug, kind, description, parameters
    ("Default", "default", "config", "Default GPN-MSA training and inference setting (three seeds).", "Default setting: 89 non-human vertebrates in the MSA, closest primates filtered, training on the most conserved regions with conserved-element upweighting and non-conserved replacement, window size 128"),
    ("w/o MSA", "without-msa", "config", "Ablation: trained only on the human sequence, without other species.", "Human sequence only; no MSA"),
    ("MSA frequency (no neural net)", "msa-frequency", "method", "Scores variants by the log-likelihood ratio of observed allele frequencies in the MSA column, with a pseudocount of 1; no neural network.", None),
    ("Combined phyloP and phastCons", "phylop-phastcons-combined", "method", "The combination of phyloP and phastCons that GPN-MSA uses to upweight its training loss, used directly as a score.", None),
    ("Train on 50% most conserved", "train-50pct-conserved", "config", "Ablation: training region expanded to the 50% most conserved windows.", "Training on the 50% most conserved windows"),
    ("Train on 100% of genome", "train-100pct-genome", "config", "Ablation: training on the whole genome.", "Training on 100% of the genome"),
    ("Include closest primates", "include-closest-primates", "config", "Ablation: the 10 primates closest to human are kept in the MSA.", "Closest 10 primates not filtered from the MSA"),
    ("51 mammals", "51-mammals", "config", "Ablation: MSA subset to 51 mammals besides human.", "MSA subset to 51 mammals"),
    ("51 vertebrates", "51-vertebrates", "config", "Ablation: MSA subset at random from 89 to 51 vertebrates besides human (bushbaby always kept).", "MSA subset to 51 vertebrates"),
    ("Don’t upweight conserved", "no-upweight-conserved", "config", "Ablation: no loss upweighting on conserved elements.", "No upweighting of conserved elements"),
    ("Don’t replace non-conserved", "no-replace-nonconserved", "config", "Ablation: the reference is not replaced with random nucleotides at non-conserved positions when computing the loss.", "No replacement of non-conserved positions"),
    ("Window size = 256", "window-256", "config", "Ablation: whole training procedure repeated with window size 256.", "Retrained with window size 256"),
    ("Window size = 64", "window-64", "config", "Ablation: default model shown a 64 bp window at prediction time.", "Default model, window 64 at variant effect prediction"),
    ("Window size = 32", "window-32", "config", "Ablation: default model shown a 32 bp window at prediction time.", "Default model, window 32 at variant effect prediction"),
    ("Window size = 16", "window-16", "config", "Ablation: default model shown a 16 bp window at prediction time.", "Default model, window 16 at variant effect prediction"),
    ("Window size = 8", "window-8", "config", "Ablation: default model shown an 8 bp window at prediction time.", "Default model, window 8 at variant effect prediction"),
    ("Window size = 4", "window-4", "config", "Ablation: default model shown a 4 bp window at prediction time.", "Default model, window 4 at variant effect prediction"),
]

start = text.index("Supplementary Table 4: Ablation study.")
end = text.index("Supplementary Table 5: Training hyperparameters")
block = text[start:end]
assert re.search(r"ClinVar\s+COSMIC\s+OMIM\s+gnomAD", block), "column groups"
assert re.search(r"mean\s+max\s+mean\s+max\s+mean\s+max\s+mean\s+max", block), "mean/max header"
assert text[:start].count("\f") + 1 == 23, "Supplementary Table 4 page"
NUM = r"(\d+\.\d+)"
parsed = {}
for label, *_ in ROWS:
    m = re.search(r"^\s*" + re.escape(label) + r"\s+" + r"\s+".join([NUM] * 8) + r"\s*$", block, re.M)
    assert m, f"row not found: {label}"
    parsed[label] = m.groups()
data_lines = [l for l in block.splitlines() if re.search(r"\d+\.\d+\s*$", l)]
assert len(data_lines) == len(ROWS) == 17, f"expected 17 data rows, got {len(data_lines)}"

COLS = [("clinvar", "ClinVar", 0, "auroc"), ("cosmic", "COSMIC", 2, "auprc"), ("omim", "OMIM", 4, "auprc")]
DATA_OF = {"clinvar": D_CLINVAR, "cosmic": D_COSMIC, "omim": D_OMIM}

for label, slug, kind, desc, params in ROWS:
    if kind == "config":
        system = add({"id": f"{P}-config-ablation-{slug}", "kind": "configuration",
                      "name": f"GPN-MSA ablation '{label}' (Supplementary Table 4)",
                      "description": desc, "status": "needs_review",
                      "facets": {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["foundation_model"]},
                      "source_ids": [S_PDF], "links": [{"relation": "configuration_of", "target_id": MODEL}],
                      "attributes": {
                          "reported_name": label,
                          "version": "Ablation model trained by the authors for bioRxiv v2 Supplementary Table 4; not a released checkpoint",
                          "parameters": params,
                          "access_reuse": "Ablation models are not listed among the published assets (gpn-msa.md); only songlab/gpn-msa-sapiens is released.",
                          "foundation_model_eligible": True,
                          "source_locator": f"Supplementary Table 4 row '{label}'; Methods 'Ablation Study'",
                      }})
        origin = "author_reported"
    else:
        system = add({"id": f"{P}-method-{slug}", "kind": "method", "name": label.replace(" (no neural net)", ""),
                      "description": desc, "status": "needs_review",
                      "facets": {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["specialist"]},
                      "source_ids": [S_PDF], "links": [],
                      "attributes": {
                          "reported_name": label,
                          "entity_level": "method",
                          "source_locator": f"Supplementary Table 4 row '{label}'; Methods 'Ablation Study'",
                          "missing_metadata": {"version": {"reason": "inapplicable", "note": "Score defined in the paper's Methods"}},
                      }})
        origin = "author_reported" if slug == "msa-frequency" else "independent_paper"
    vals = parsed[label]
    for key, colname, idx, metric in COLS:
        ev = add({"id": f"{P}-eval-ablation-{slug}-{key}", "kind": "evaluation",
                  "name": f"{label} on {colname} (GPN-MSA Supplementary Table 4)",
                  "description": "Published comparison transcribed from the pinned source; not reproduced.",
                  "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF],
                  "links": [{"relation": "system", "target_id": system},
                            {"relation": "assessment", "target_id": PROTO[key]},
                            {"relation": "data", "target_id": DATA_OF[key]}],
                  "attributes": {
                      "origin": origin,
                      "protocol": PROTO[key],
                      "version": "bioRxiv v2 as retrieved 2026-10-14",
                      "comparison": {"protocol_id": PROTO[key], "dataset_version": None, "split": "Whole labelled set",
                                     "population": None, "inputs": "Reference genome and multispecies alignment around each variant (GPN-MSA rows); alignment column or conservation scores (method rows)",
                                     "adaptation": "zero-shot", "metric_implementation": None,
                                     "aggregation": "Mean and maximum over three random seeds where applicable (printed as separate columns)",
                                     "budget": None},
                      "source_locator": f"Supplementary Table 4 row '{label}', column group '{colname}'",
                      "missing_metadata": {"comparison.dataset_version": {"reason": "unreported", "note": "Release versions are printed in Methods but the scored variant set and its size are not"},
                                           "comparison.population": {"reason": "unreported"},
                                           "comparison.metric_implementation": {"reason": "unreported"},
                                           "comparison.budget": {"reason": "unreported"}},
                  }})
        for agg, off in [("mean", 0), ("max", 1)]:
            pv = vals[idx + off]
            rid = f"{P}-result-ablation-{slug}-{key}-{agg}"
            loc = f"Supplementary Table 4 (PDF page 23), row '{label}', column '{colname}' / '{agg}'"
            add({"id": rid, "kind": "result",
                 "name": f"{label} {colname} {metric.upper()} ({agg} over seeds)",
                 "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                 "status": "needs_review", "facets": {}, "source_ids": [S_PDF],
                 "links": [{"relation": "evaluation", "target_id": ev}],
                 "attributes": {
                     "printed_value": pv, "numeric_value": pv,
                     "metric": metric, "metric_direction": "higher", "unit": "unitless",
                     "metric_qualifier": ("mean over three random seeds" if agg == "mean" else "maximum over three random seeds") + "; zero-shot",
                     "source_locator": loc,
                     "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Only mean and max over seeds are printed"}},
                     "review": review(["pdf-text-parse"],
                                      "Extracted, not reviewed. For rows without a neural network (MSA frequency, combined phyloP and phastCons) three seeds do not apply and mean equals max. The review-evidence pass must re-check this cell against the pinned PDF.",
                                      method_note="Parsed the pdftotext 26.08.0 -layout text of the pinned PDF with extract/build_gpnmsa.py; header groups, 'mean max' header, the 17 row labels and the page are asserted."),
                 }})
            claims_rows.append([rid, S_PDF, loc, pv, "result"])

# ---------------------------------------------------------------- DMS TADBP text values
sent = "TADBP, for which GPN-MSA AUROC is 0.83, while ESM-1b AUROC is 0.75"
flat = re.sub(r"\s+", " ", text)
assert sent in flat, "TADBP sentence"
assert text[:text.index("TADBP, for which")].count("\f") + 1 == 6
C_MAIN = add({"id": f"{P}-config-gpn-msa-main", "kind": "configuration", "name": "GPN-MSA, main results model (bioRxiv v2)",
              "description": "GPN-MSA as used for the paper's main variant effect results; log-likelihood ratio averaged over both strands.",
              "status": "needs_review",
              "facets": {"areas": ["dna-genomes"], "contexts": ["research"], "method_types": ["foundation_model"]},
              "source_ids": [S_PDF, S_DOC], "links": [{"relation": "configuration_of", "target_id": MODEL}],
              "attributes": {
                  "reported_name": "GPN-MSA",
                  "parameters": "Log-likelihood ratio between alternate and reference allele, averaged over both strands",
                  "access_reuse": "Published checkpoint songlab/gpn-msa-sapiens (gpn-msa.md); the preprint does not say which seed or checkpoint produced the DMS values",
                  "foundation_model_eligible": True,
                  "source_locator": "Methods 'VEP scores' (GPN-MSA); Results DMS paragraph",
                  "missing_metadata": {"version": {"reason": "unreported", "note": "Not stated whether the released checkpoint or one of the default-setting seeds was used"}},
              }})
C_ESM = add({"id": f"{P}-config-esm-1b-precomputed-llr", "kind": "configuration",
             "name": "ESM-1b, precomputed log-likelihood ratios (GPN-MSA paper)",
             "description": "ESM-1b precomputed log-likelihood ratios in protein coordinates (from Brandes et al.), minimum over isoforms, as used in the GPN-MSA paper.",
             "status": "needs_review",
             "facets": {"areas": ["protein-function"], "contexts": ["research"], "method_types": ["foundation_model"]},
             "source_ids": [S_PDF], "links": [{"relation": "configuration_of", "target_id": ESM1B_MODEL}],
             "attributes": {
                 "reported_name": "ESM-1b",
                 "parameters": "Precomputed log-likelihood ratio between alternate and reference amino acid (reference [6] of the preprint, Brandes et al.); for variants affecting multiple isoforms, the minimum score",
                 "access_reuse": "Precomputed scores from the Brandes et al. release",
                 "foundation_model_eligible": True,
                 "source_locator": "Methods 'VEP scores' (ESM-1b)",
                 "missing_metadata": {"version": {"reason": "unreported", "note": "Score release and checkpoint not named in the GPN-MSA preprint"}},
             }})
for system, slug, label, pv, origin in [(C_MAIN, "gpn-msa", "GPN-MSA", "0.83", "author_reported"),
                                        (C_ESM, "esm-1b", "ESM-1b", "0.75", "independent_paper")]:
    ev = add({"id": f"{P}-eval-dms-tadbp-{slug}", "kind": "evaluation",
              "name": f"{label} on ProteinGym DMS TADBP binary classification (GPN-MSA paper)",
              "description": "Published comparison transcribed from the pinned source; not reproduced.",
              "status": "needs_review", "facets": {"areas": ["dna-genomes", "protein-function"], "contexts": ["research"]},
              "source_ids": [S_PDF],
              "links": [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": P_TADBP},
                        {"relation": "data", "target_id": D_TADBP}],
              "attributes": {
                  "origin": origin, "protocol": P_TADBP, "version": "bioRxiv v2 as retrieved 2026-10-14",
                  "comparison": {"protocol_id": P_TADBP, "dataset_version": "ProteinGym v0.1", "split": "Whole assay",
                                 "population": None, "inputs": "Genomic context (GPN-MSA) or protein sequence (ESM-1b)",
                                 "adaptation": "zero-shot", "metric_implementation": None, "aggregation": None, "budget": None},
                  "source_locator": "Results paragraph beginning 'We also evaluate on deep mutational scanning' (PDF page 6)",
                  "missing_metadata": {"comparison.population": {"reason": "unreported"},
                                       "comparison.metric_implementation": {"reason": "unreported"},
                                       "comparison.aggregation": {"reason": "inapplicable", "note": "Single assay"},
                                       "comparison.budget": {"reason": "unreported"}},
              }})
    rid = f"{P}-result-dms-tadbp-{slug}-auroc"
    loc = f"Results paragraph beginning 'We also evaluate on deep mutational scanning', sentence 'Nevertheless, GPN-MSA performs better than ESM-1b on some proteins (e.g., TADBP, for which GPN-MSA AUROC is 0.83, while ESM-1b AUROC is 0.75)' (PDF page 6)"
    add({"id": rid, "kind": "result", "name": f"{label} DMS TADBP AUROC",
         "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
         "status": "needs_review", "facets": {}, "source_ids": [S_PDF],
         "links": [{"relation": "evaluation", "target_id": ev}],
         "attributes": {
             "printed_value": pv, "numeric_value": pv, "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
             "metric_qualifier": "binary labels from absolute relative toxicity > 0.125; zero-shot",
             "source_locator": loc,
             "missing_metadata": {"uncertainty": {"reason": "unreported"}},
             "review": review(["transcription"], "Extracted, not reviewed. Value quoted in the Results text; the per-assay figure (Supplementary Figure 5) was not read.",
                              method_note="Transcribed from the PDF text layer; extract/build_gpnmsa.py asserts the sentence verbatim and its page."),
         }})
    claims_rows.append([rid, S_PDF, loc, pv, "result"])

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids))
with open(f"{OUT}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(f"{OUT}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for row in sorted(claims_rows):
        w.writerow(row)
from collections import Counter
print(Counter(r["kind"] for r in records))
