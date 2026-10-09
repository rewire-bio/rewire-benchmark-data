"""Deterministic extraction for the patient-RNA splicing use-case pass, 2026-10-09.

Usage: python3 -I extract_rna_splicing.py <download-dir> <batch-dir>

<download-dir> holds the Europe PMC downloads, one folder per PMCID:
  PMC12547740/fulltext.xml and PMC12547740/supp/mmc2.xlsx  (Drost et al., HGG Advances)
  PMC12257123/fulltext.xml                                  (Segarra-Casas et al., ACTN)
  PMC13019952/fulltext.xml                                  (Segers et al., Genome Biology)

Writes batch.jsonl and claims.csv to <batch-dir>. Every cell of Data S1 Tables S3 and S4
(Drost), Table 2 (Segarra-Casas) and Table 2 (Segers) becomes one result; row and column
labels are asserted before any value is read.
"""
import csv, hashlib, json, os, sys, xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

DL, OUT = sys.argv[1], sys.argv[2]
P = "rna-splicing-20261009"
UC = "use-case-patient-rna-splicing-validation"
DATE = "2026-10-09"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def txt(e):
    return " ".join("".join(e.itertext()).split())


def shortest(raw):
    """Shortest decimal that round-trips to the stored IEEE double."""
    v = float(raw)
    s = repr(v)
    if "e" in s or "E" in s:
        s = format(v, "f")
    return s


records, claims_rows = [], []


def rec(kind, id_, name, description, attributes, source_ids, links=(), facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": facets if facets is not None else {}, "source_ids": list(source_ids),
         "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attributes}
    records.append(r)
    return r


FAC_DNA = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
FAC_RNA = {"areas": ["rna-transcriptomes"], "contexts": ["clinical_research"]}

# ---------------------------------------------------------------- sources
art = {
    "drost": os.path.join(DL, "PMC12547740", "fulltext.xml"),
    "drost_s1": os.path.join(DL, "PMC12547740", "supp", "mmc2.xlsx"),
    "drost_zip": os.path.join(DL, "PMC12547740", "supp.zip"),
    "segarra": os.path.join(DL, "PMC12257123", "fulltext.xml"),
    "segers": os.path.join(DL, "PMC13019952", "fulltext.xml"),
}
H = {k: sha(v) for k, v in art.items()}

S_DROST, S_DROST1 = f"{P}-source-drost2025", f"{P}-source-drost2025-data-s1"
S_SEG, S_SASER = f"{P}-source-segarracasas2025", f"{P}-source-segers2026"
URL = {
    S_DROST: EPMC + "PMC12547740/fullTextXML",
    S_DROST1: EPMC + "PMC12547740/supplementaryFiles",
    S_SEG: EPMC + "PMC12257123/fullTextXML",
    S_SASER: EPMC + "PMC13019952/fullTextXML",
}
SHA = {S_DROST: H["drost"], S_DROST1: H["drost_s1"], S_SEG: H["segarra"], S_SASER: H["segers"]}

rec("source", S_DROST,
    "Routine RNA-based analysis of potential splicing variants facilitates genomic diagnostics and reveals limitations of in silico prediction tools",
    "Primary source retrieved and hashed for the patient-RNA splicing use-case pass.",
    {"url": "https://doi.org/10.1016/j.xhgg.2025.100521", "artifact_url": URL[S_DROST],
     "version": "HGG Advances 7(1):100521, published online 2025-09-22; PMC12547740 full-text XML",
     "retrieved_at": "2026-10-09T20:30:41Z", "artifact_sha256": H["drost"], "doi": "10.1016/j.xhgg.2025.100521",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml",
     "evidence_concerns": [{
         "source_id": S_DROST,
         "message": "Results ('Additional splicing prediction tools can help predict variant effect on splicing', paragraph 2) prints SQUIRLS AUPRC 0.888, but Data S1 Table S3 D13 stores 0.88147692899705499 (0.881). The other prose AUROC/AUPRC values agree with Table S3 after truncation. The same section cites Table S3 for thresholded TPR, F1 and NPV, which are in Table S4. Table values are recorded.",
         "source_locator": "Results, 'Additional splicing prediction tools can help predict variant effect on splicing', paragraphs 2 and 3, versus Data S1 Table S3 D13 and Table S4",
         "artifact_sha256": H["drost"], "reviewed_at": "2026-10-09T21:00:00Z", "review_method": "ai-assisted-source-review"}]},
    [], facets=FAC_DNA)
rec("source", S_DROST1, "Drost et al. 2025, Data S1 (Tables S1-S6)",
    "Supplementary workbook holding the per-tool splice-prediction performance tables.",
    {"url": "https://doi.org/10.1016/j.xhgg.2025.100521", "artifact_url": URL[S_DROST1],
     "version": "mmc2.xlsx (Data S1. Tables S1-S6) inside the Europe PMC supplementaryFiles zip for PMC12547740",
     "retrieved_at": "2026-10-09T20:31:37Z", "artifact_sha256": H["drost_s1"], "doi": "10.1016/j.xhgg.2025.100521",
     "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
     "hash_scope": f"SHA-256 of mmc2.xlsx as extracted from the supplementaryFiles zip (zip SHA-256 {H['drost_zip']}; the zip is re-built by Europe PMC on each request, so only the member hash is stable)."},
    [], facets=FAC_DNA)
rec("source", S_SEG, "Translating Muscle RNAseq Into the Clinic for the Diagnosis of Muscle Diseases",
    "Primary source retrieved and hashed for the patient-RNA splicing use-case pass.",
    {"url": "https://doi.org/10.1002/acn3.70078", "artifact_url": URL[S_SEG],
     "version": "Annals of Clinical and Translational Neurology 12(7):1465, published online 2025-05-25; PMC12257123 full-text XML",
     "retrieved_at": "2026-10-09T20:33:50Z", "artifact_sha256": H["segarra"], "doi": "10.1002/acn3.70078",
     "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml"},
    [], facets=FAC_RNA)
rec("source", S_SASER,
    "saseR: juggling offsets unlocks RNA-seq tools for fast and scalable differential usage, aberrant splicing and expression retrieval",
    "Primary source retrieved and hashed for the patient-RNA splicing use-case pass.",
    {"url": "https://doi.org/10.1186/s13059-026-03973-8", "artifact_url": URL[S_SASER],
     "version": "Genome Biology 27:103, published online 2026-02-18; PMC13019952 full-text XML",
     "retrieved_at": "2026-10-09T20:30:42Z", "artifact_sha256": H["segers"], "doi": "10.1186/s13059-026-03973-8",
     "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml"},
    [], facets=FAC_RNA)

# ---------------------------------------------------------------- methods
def method(short, name, desc, srcs, locator, access=None, facets=FAC_RNA, mtype="conventional_pipeline"):
    a = {"reported_name": name, "entity_level": "method", "source_locator": locator,
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
    if access:
        a["access"] = access
    f = dict(facets, method_types=[mtype])
    return rec("method", f"{P}-method-{short}", name, desc, a, srcs, facets=f)["id"]


M = {}
M["spip"] = method("spip", "SPiP", "Splicing Prediction Pipeline; variant-level splice-effect predictor.", [S_DROST],
                   "Methods, 'In silico splice predictions'", facets=FAC_DNA, mtype="supervised_machine_learning")
M["squirls"] = method("squirls", "SQUIRLS", "Super-quick information-content and random-forest learning of splice variants.", [S_DROST],
                      "Methods, 'In silico splice predictions'; Web resources (https://github.com/monarch-initiative/Squirls)",
                      facets=FAC_DNA, mtype="supervised_machine_learning")
M["consensus"] = method("splice-predictor-consensus", "At-least-N consensus of SpliceAI, Pangolin, SPiP and SQUIRLS",
                        "Heuristic combination defined by Drost et al.: a variant is predicted to affect splicing when at least N of the four tools exceed their literature thresholds.",
                        [S_DROST, S_DROST1], "Results, 'Additional splicing prediction tools...' paragraph 3; Data S1 Table S4 rows AtLeast1-AtLeast4",
                        facets=FAC_DNA)
GH = "Open-source code on GitHub, as listed in the Segarra-Casas et al. Data Availability Statement"
M["fraser"] = method("fraser", "FRASER", "Count-based aberrant-splicing outlier caller for RNA-seq cohorts (FRASER 1.x and FRASER 2.0 / FRASER2 with the intron Jaccard index).",
                     [S_SEG, S_SASER], "Segarra-Casas et al. Methods 'Aberrant Splicing' and Data Availability; Segers et al. Results 'Detection of aberrant splicing'", access=GH)
M["leafcuttermd"] = method("leafcuttermd", "LeafCutterMD", "Dirichlet-multinomial splicing outlier caller from the LeafCutter package.",
                           [S_SEG], "Methods 'Aberrant Splicing'; Data Availability", access=GH)
M["rmats"] = method("rmats-turbo", "rMATS-turbo", "Replicate multivariate analysis of transcript splicing (turbo implementation).",
                    [S_SEG], "Methods 'Aberrant Splicing'; Data Availability", access=GH)
M["outrider"] = method("outrider", "OUTRIDER", "Negative-binomial autoencoder (or PCA) aberrant-expression outlier caller.",
                       [S_SEG, S_SASER], "Segarra-Casas et al. Methods 'Gene Expression'; Segers et al. Results 'Detection of aberrant expression'", access=GH)
M["outsingle"] = method("outsingle", "OutSingle", "Log-normal approximation aberrant-expression outlier caller.",
                        [S_SASER], "Segers et al. Background and Results 'Detection of aberrant expression'")
M["saser"] = method("saser", "saseR", "Offset-based negative-binomial framework for differential usage, aberrant expression and aberrant splicing.",
                    [S_SASER], "Segers et al. Results and Conclusions", access="Available on GitHub (https://github.com/statOmics/saseR/) and Bioconductor, per Segers et al. Conclusions")

# ---------------------------------------------------------------- configurations
def config(short, name, desc, of, srcs, mtype, version=None, version_note=None, params=None, locator=None, facets=FAC_RNA, limitations=None):
    a = {"reported_name": name, "foundation_model_eligible": False}
    if version:
        a["version"] = version
    else:
        a["missing_metadata"] = {"version": {"reason": "unreported", "note": version_note}}
    if params:
        a["parameters"] = params
    if locator:
        a["source_locator"] = locator
    if limitations:
        a["limitations"] = limitations
    return rec("configuration", f"{P}-config-{short}", name, desc, a, srcs,
               links=[("configuration_of", of)], facets=dict(facets, method_types=[mtype]))["id"]


DS = [S_DROST, S_DROST1]
C = {}
C["d_spliceai"] = config("drost2025-spliceai", "SpliceAI (Drost et al.)", "SpliceAI precomputed scores as used by Drost et al.",
                         "catalog-model-spliceai", DS, "supervised_machine_learning",
                         version_note="SpliceAI release not printed; precomputed scores were taken from WGSA version 0.95, with missing annotations filled from the SpliceAI Lookup web page.",
                         params="Binary predictions at the literature threshold 0.12", locator="Methods 'In silico splice predictions'; Results paragraph 3", facets=FAC_DNA)
C["d_pangolin"] = config("drost2025-pangolin", "Pangolin (Drost et al.)", "Pangolin as used by Drost et al.",
                         "catalog-model-pangolin", DS, "supervised_machine_learning", version="version 4.3.1 (as printed)",
                         params="Binary predictions at the literature threshold 0.106", locator="Methods 'In silico splice predictions'; Results paragraph 3", facets=FAC_DNA,
                         limitations=["The printed Pangolin version 4.3.1 does not match the tkzeng/Pangolin release numbering known to the extractor; recorded as printed, not resolved."])
C["d_spip"] = config("drost2025-spip", "SPiP 2.1 (Drost et al.)", "SPiP as used by Drost et al.", M["spip"], DS, "supervised_machine_learning",
                     version="2.1", params="Binary predictions at the literature threshold 0.452", locator="Methods 'In silico splice predictions'; Results paragraph 3", facets=FAC_DNA)
C["d_squirls"] = config("drost2025-squirls", "SQUIRLS 2.0.1 (Drost et al.)", "SQUIRLS as used by Drost et al.", M["squirls"], DS, "supervised_machine_learning",
                        version="2.0.1", params="Binary predictions at the literature threshold 0.018", locator="Methods 'In silico splice predictions'; Results paragraph 3", facets=FAC_DNA)
for n in range(1, 5):
    C[f"d_al{n}"] = config(f"drost2025-at-least-{n}", f"At least {n} of 4 splice predictors (Drost et al.)",
                           f"Effect predicted when at least {n} of SpliceAI, Pangolin, SPiP and SQUIRLS exceed their literature thresholds.",
                           M["consensus"], DS, "conventional_pipeline", version=f"AtLeast{n} (as printed)",
                           params="Component thresholds: SQUIRLS 0.018, SPiP 0.452, Pangolin 0.106, SpliceAI 0.12",
                           locator=f"Data S1 Table S4 row label 'AtLeast{n}'; Results paragraph 3", facets=FAC_DNA)

SG = [S_SEG]
C["s_fraser01"] = config("segarracasas2025-fraser-dpsi-0-1", "FRASER v1.8.1, |dPSI| > 0.1 (Segarra-Casas et al.)", "FRASER with effect-size cutoff |delta PSI| > 0.1.",
                         M["fraser"], SG, "conventional_pipeline", version="v1.8.1", params="|delta PSI| > 0.1; analysis restricted to neuromuscular-disease genes",
                         locator="Methods 'Aberrant Splicing'; Table 2 column header")
C["s_fraser03"] = config("segarracasas2025-fraser-dpsi-0-3", "FRASER v1.8.1, |dPSI| > 0.3 (Segarra-Casas et al.)", "FRASER with effect-size cutoff |delta PSI| > 0.3.",
                         M["fraser"], SG, "conventional_pipeline", version="v1.8.1", params="|delta PSI| > 0.3; analysis restricted to neuromuscular-disease genes",
                         locator="Methods 'Aberrant Splicing'; Table 2 column header")
C["s_fraser2"] = config("segarracasas2025-fraser2", "FRASER2 v1.99.4 (Segarra-Casas et al.)", "FRASER2 (intron Jaccard index release).",
                        M["fraser"], SG, "conventional_pipeline", version="v1.99.4", params="Analysis restricted to neuromuscular-disease genes",
                        locator="Methods 'Aberrant Splicing'; Data Availability (release tag 1.99.4)")
C["s_leafcutter"] = config("segarracasas2025-leafcuttermd", "LeafCutterMD v0.2.7 (Segarra-Casas et al.)", "LeafCutterMD as run by Segarra-Casas et al.",
                           M["leafcuttermd"], SG, "conventional_pipeline", version="v0.2.7", locator="Methods 'Aberrant Splicing'")
C["s_rmats"] = config("segarracasas2025-rmats-turbo", "rMATS-turbo v4.1.2 (Segarra-Casas et al.)", "rMATS-turbo as run by Segarra-Casas et al.",
                      M["rmats"], SG, "conventional_pipeline", version="v4.1.2", locator="Methods 'Aberrant Splicing'")
C["s_outrider"] = config("segarracasas2025-outrider", "OUTRIDER v1.20.1 (Segarra-Casas et al.)", "OUTRIDER on StringTie gene counts.",
                         M["outrider"], SG, "conventional_pipeline", version="v1.20.1", locator="Methods 'Gene Expression'")

SS = [S_SASER]
NOV = "No software version printed in the article or Additional file 1."
C["g_saser_expr"] = config("segers2026-saser-expression", "saseR, aberrant expression (Segers et al.)", "saseR on gene counts for aberrant expression.",
                           M["saser"], SS, "conventional_pipeline", version_note=NOV, locator="Table 2 column 'Aberrant expression: saseR'")
C["g_outsingle"] = config("segers2026-outsingle", "OutSingle (Segers et al.)", "OutSingle as run by Segers et al.",
                          M["outsingle"], SS, "conventional_pipeline", version_note=NOV, locator="Table 2 column 'OutSingle'")
C["g_outrider_auto"] = config("segers2026-outrider-autoencoder", "OUTRIDER autoencoder (Segers et al.)", "OUTRIDER with its negative-binomial autoencoder.",
                              M["outrider"], SS, "conventional_pipeline", version_note=NOV, locator="Table 2 column 'OUTRIDER AUTO'")
C["g_outrider_pca"] = config("segers2026-outrider-pca", "OUTRIDER PCA (Segers et al.)", "OUTRIDER with principal component analysis on log-transformed counts.",
                             M["outrider"], SS, "conventional_pipeline", version_note=NOV, locator="Table 2 column 'OUTRIDER PCA'")
C["g_saser_junc"] = config("segers2026-saser-junctions", "saseR-junctions (Segers et al.)", "saseR on junction reads with the log total junction count per gene as offset.",
                           M["saser"], SS, "conventional_pipeline", version_note=NOV, locator="Table 2 column 'Aberrant splicing: saseR junctions'")
C["g_fraser2_auto"] = config("segers2026-fraser2-autoencoder", "FRASER 2.0 autoencoder (Segers et al.)", "FRASER 2.0 (intron Jaccard index) with the autoencoder latent-factor fit.",
                             M["fraser"], SS, "conventional_pipeline", version_note=NOV, params="Hyperparameter optimisation with the PCA implementation, as stated for FRASER runs",
                             locator="Table 2 column 'FRASER 2.0 AUTO'; Results 'Detection of aberrant splicing' paragraph 1")
C["g_fraser2_pca"] = config("segers2026-fraser2-pca", "FRASER 2.0 PCA (Segers et al.)", "FRASER 2.0 (intron Jaccard index) with the PCA latent-factor fit.",
                            M["fraser"], SS, "conventional_pipeline", version_note=NOV, locator="Table 2 column 'FRASER 2.0 PCA'")

# ---------------------------------------------------------------- datasets
D = {}
D["merged"] = rec("dataset", f"{P}-data-drost2025-merged-243", "Drost et al. RNA-tested clinical variants plus CAGI6 Splicing VUS, 243 scorable",
                  "Variants tested for splicing in patient RNA (RT-PCR) or exon trapping in a Dutch diagnostic laboratory, merged with the CAGI6 Splicing VUS set, restricted to variants scored by all four tools.",
                  {"version": "Data S1 Table S2 (as published)", "variants": 243,
                   "population": "202 in-house variants tested 2015-2023 in patient or relative RNA (RT-PCR, Sanger) and/or exon trapping, plus 56 CAGI6 Splicing VUS challenge variants; 243 variants scored by all four tools, including all 56 CAGI6 variants.",
                   "split": "No training split; evaluation of pretrained or rule-based predictors on the whole set",
                   "source_locator": "Results 'Additional splicing prediction tools...' paragraph 1; Results 'RNA splicing analysis reclassifies 54% of VUS' paragraphs 1-3",
                   "missing_metadata": {"positives": {"reason": "unreported", "note": "Positive/negative counts for the 243 are not printed; Table S4 ratios are consistent with 155 and 88 (derived, not stored)."}}},
                  DS, facets=FAC_DNA)["id"]
D["cagi6"] = rec("dataset", f"{P}-data-drost2025-cagi6-subset", "CAGI6 Splicing VUS variants as scored by Drost et al.",
                 "The 56 clinically ascertained, functionally validated CAGI6 Splicing VUS challenge variants included in the Drost et al. comparison.",
                 {"version": "CAGI6 Splicing VUS challenge set as used in Data S1", "variants": 56,
                  "population": "56 curated CAGI6 Splicing VUS variants, all scored by the four tools",
                  "split": "Cohort stratum of the 243-variant comparison", "source_locator": "Results 'Additional splicing prediction tools...' paragraph 1; Data S1 Table S3 'CAGI6' rows and Table S4 'CAGI6 dataset'"},
                 DS, facets=FAC_DNA)["id"]
D["inhouse"] = rec("dataset", f"{P}-data-drost2025-inhouse-subset", "Drost et al. in-house RNA-tested diagnostic variants, scorable subset",
                   "In-house diagnostic variants of the Drost et al. cohort that were scored by all four tools.",
                   {"version": "Data S1 Table S2 (as published)",
                    "population": "Variants submitted for diagnostic splicing analysis at Erasmus MC 2015-2023, tested in patient RNA from blood, fibroblasts or other tissue (RT-PCR) and/or exon trapping; 87% (176/202) were selected because Alamut Visual Plus predicted a splicing change.",
                    "split": "Cohort stratum of the 243-variant comparison",
                    "source_locator": "Results 'RNA splicing analysis reclassifies 54% of VUS' paragraph 1; Data S1 Table S3 'In House' rows and Table S4 'In House dataset'",
                    "missing_metadata": {"variants": {"reason": "unreported", "note": "Scorable in-house count not printed; 243 minus 56 CAGI6 gives 187 (derived, not stored)."}}},
                   DS, facets=FAC_DNA)["id"]
D["muscle"] = rec("dataset", f"{P}-data-segarracasas2025-muscle-rnaseq", "Segarra-Casas et al. skeletal-muscle RNA-seq cohort, 16 pathogenic splicing events",
                  "Clinical muscle-biopsy RNA-seq from individuals with suspected muscle disease and no diagnosis after exome sequencing.",
                  {"version": "As published (raw data not shared)", "assay": "Total RNA, Illumina Stranded Total RNA Prep with Ribo-Zero Plus, NovaSeq 6000 150 bp paired-end; HISAT2 to GRCh37",
                   "population": "98 muscle RNA-seq samples in three sequencing batches (batch 1: 34 samples, 29 cases and 5 controls); 70 participants with suspected muscle disease per the Introduction; 16 pathogenic splicing alterations identified across all 98 samples.",
                   "split": "No split; retrospective detection of known events",
                   "reuse_restrictions": "Raw data not publicly available (ethics); available from the corresponding author on reasonable request",
                   "source_locator": "Introduction paragraph 3; Methods 'RNA Extraction, Library Preparation, and Sequencing' and 'RNAseq Data Analysis'; Results 'Aberrant Splicing Detection' paragraphs 1 and 3; Data Availability"},
                  SG, facets=FAC_RNA)["id"]
KREMER = "amp-oncology-rna-20261007-dataset-kremer-patient-rna"

# ---------------------------------------------------------------- protocols
def protocol(short, name, desc, srcs, data, attrs, facets):
    return rec("protocol", f"{P}-protocol-{short}", name, desc, attrs, srcs, links=[("uses_data", data)], facets=facets)["id"]


DROST_PROTO = ("Score each variant with SpliceAI, Pangolin, SPiP and SQUIRLS; truth is the experimental result in patient RNA (RT-PCR and Sanger) or exon trapping "
               "(effect on splicing versus no effect). AUROC (plotROC) and AUPRC (yardstick) from continuous scores; sensitivity, specificity, precision, F1, PPV and NPV "
               "(caret) after binarising at literature thresholds (SQUIRLS 0.018, SPiP 0.452, Pangolin 0.106, SpliceAI 0.12), and for at-least-N consensus rules.")
DROST_LIM = [
    "Ascertainment: 87% of in-house variants were sent for RNA testing because Alamut predicted a splicing change, so negatives are mostly predicted-but-unconfirmed variants.",
    "Restricted to variants scorable by all four tools; per-tool missing scores are not counted as negatives.",
    "Variant-level splicing effect, not pathogenicity; tissue was chosen per gene (blood, fibroblasts or exon trapping), not modelled by the predictors.",
    "Literature thresholds, not tuned on this set; AUROC/AUPRC have no printed uncertainty.",
]
PR = {}
for key, short, label, data, loc in (
        ("merged", "drost2025-merged-243", "all 243 scorable variants", D["merged"], "Data S1 Table S3 'Entire Dataset' (B9:D13); Table S4 'Entire Dataset' (B6:H15)"),
        ("inhouse", "drost2025-inhouse", "in-house diagnostic cohort", D["inhouse"], "Data S1 Table S3 'Stratified datasets', Dataset 'In House' (F12:I15); Table S4 'In House dataset' (B32:H41)"),
        ("cagi6", "drost2025-cagi6", "CAGI6 Splicing VUS subset", D["cagi6"], "Data S1 Table S3 'Stratified datasets', Dataset 'CAGI6' (F7:I10); Table S4 'CAGI6 dataset' (B19:H28)")):
    PR[key] = protocol(short, f"Splice-effect prediction against patient-RNA or exon-trapping results, {label} (Drost et al. Data S1)",
                       "Variant-level classification of experimentally tested splicing effect by DNA-based splice predictors.", DS, data,
                       {"protocol": DROST_PROTO, "version": "Data S1 Tables S3 and S4", "source_locator": loc, "limitations": DROST_LIM,
                        "missing_metadata": {"metric_implementation": {"reason": "unextracted", "note": "R code not published with the article; packages plotROC 2.3.1, yardstick 1.2.0 and caret 6.0.94 are named"}}},
                       FAC_DNA)
PR["muscle_splice"] = protocol("segarracasas2025-known-event-detection", "Detection of 16 known pathogenic splicing events in clinical muscle RNA-seq (Segarra-Casas et al. Table 2)",
                               "Whether each aberrant-splicing caller reported each established pathogenic splicing alteration as an outlier.", SG, D["muscle"],
                               {"protocol": "Run each caller on the muscle RNA-seq cohort, restricted to neuromuscular-disease genes; record Yes/No per known pathogenic splicing alteration (16 events in 15 cases, including two events in case 63 and the same CAPN3 variant in cases 37 and 69).",
                                "version": "Table 2", "source_locator": "Table 2 columns 'FRASER |dPSI| > 0.1' to 'rMATS-turbo'",
                                "limitations": [
                                    "Events are those the authors established, partly with these same callers, so recall is measured on events at least one method could reveal.",
                                    "Cohort size per run is not stated in Table 2; Results imply the full 98-sample cohort, and the footnote marks the FRASER2 call for case 2 as found only with all cohort samples (missed in batch 1, n = 34).",
                                    "LeafCutterMD is not designed to report intron retention, which was part of five events (Discussion).",
                                    "No false-positive or per-sample workload counts in the table; outlier counts per sample are figure-only (Figure 2A).",
                                    "Prose detection rates conflict: Results give FRASER2 68.7% (11/16), Discussion gives 66.6%."],
                                "missing_metadata": {"denominator": {"reason": "unreported", "note": "Samples analysed per caller run not printed in Table 2"}}},
                               FAC_RNA)
PR["muscle_expr"] = protocol("segarracasas2025-outrider-zscore", "OUTRIDER expression z-score at 16 known pathogenic splicing events in muscle RNA-seq (Segarra-Casas et al. Table 2)",
                             "Aberrant-expression z-score of the affected gene in the sample carrying each known pathogenic splicing alteration.", SG, D["muscle"],
                             {"protocol": "OUTRIDER on StringTie gene counts; z-score printed for the gene of each known pathogenic splicing event; bold marks a correct identification as aberrant outlier (table footnote).",
                              "version": "Table 2", "source_locator": "Table 2 column 'Aberrant expression (OUTRIDER z-score)'",
                              "limitations": ["Expression outlier status is indirect evidence for a splicing defect (for example via nonsense-mediated decay); in-frame events are not expected to change expression.",
                                              "Outlier significance threshold is not printed in the table; bold formatting is the only call indicator."]},
                             FAC_RNA)
PR["kremer_splice"] = protocol("segers2026-kremer-splicing-rank", "Rank of known disease genes in 12 Kremer fibroblast RNA samples, aberrant splicing (Segers et al. Table 2)",
                               "Rank of each reported disease gene among the genes of the patient's sample by aberrant-splicing score.", SS, KREMER,
                               {"protocol": "Single analysis of the 119-sample Kremer fibroblast junction-count compendium (FRASER paper Zenodo release, FRASER standard filtering, 79,077 junctions); rank of the score of the disease-related gene validated in each of 12 patient samples (TIMMDC1 counted twice for two patients).",
                                "version": "Table 2", "source_locator": "Table 2 'Aberrant splicing' columns; Results 'Case study: Kremer dataset' paragraph 1; Methods 'Data'",
                                "limitations": ["Developer comparison: saseR authors ran FRASER 2.0.",
                                                "Disease genes include expression and mono-allelic-expression cases (for example ALDH18A1, MCOLN1), not only splicing defects.",
                                                "Same cohort used to develop and report FRASER; genes were reported in earlier Kremer, Brechtmann and Mertes analyses.",
                                                "LeafCutterMD and SPOT were not run on Kremer because only junction counts are public."],
                                "missing_metadata": {"metric_definition": {"reason": "unreported", "note": "Tie handling and total genes ranked per sample not printed"}}},
                               FAC_RNA)
PR["kremer_expr"] = protocol("segers2026-kremer-expression-rank", "Rank of known disease genes in 12 Kremer fibroblast RNA samples, aberrant expression (Segers et al. Table 2)",
                             "Rank of each reported disease gene among the genes of the patient's sample by aberrant-expression score.", SS, KREMER,
                             {"protocol": "Single analysis of 119 Kremer fibroblast gene-count samples (14,379 genes after filtering); rank of the score of the disease-related gene in each of 12 patient samples.",
                              "version": "Table 2", "source_locator": "Table 2 'Aberrant expression' columns; Results 'Case study: Kremer dataset'; Methods 'Data'",
                              "limitations": ["Developer comparison: saseR authors ran OUTRIDER and OutSingle.",
                                              "Expression outliers are indirect evidence for splice-altering variants."],
                              "missing_metadata": {"metric_definition": {"reason": "unreported", "note": "Tie handling and total genes ranked per sample not printed"}}},
                             FAC_RNA)

# ---------------------------------------------------------------- evaluations and results
def evaluation(short, name, cfg, proto, data, srcs, origin, comparison, locator, facets, limitations=None, missing=None):
    a = {"origin": origin, "protocol": proto, "version": "Primary source as retrieved 2026-10-09",
         "comparison": dict(comparison, protocol_id=proto), "source_locator": locator}
    if limitations:
        a["limitations"] = limitations
    if missing:
        a["missing_metadata"] = missing
    return rec("evaluation", f"{P}-eval-{short}", name, "Published comparison; transcribed, not reproduced.", a, srcs,
               links=[("system", cfg), ("assessment", proto), ("data", data)], facets=facets)["id"]


def review_obj(src, method, how):
    return {"method": [method], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
            "date": DATE, "artifact_sha256": SHA[src], "retrieval_url": URL[src],
            "note": how + " Pending independent review."}


def result(short, ev, srcs, src_hash_id, metric, direction, unit, printed, numeric, qualifier, locator, how, method,
           unit_detail=None, raw=None, printed_cell=None, unc_reason="unreported"):
    a = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed, "numeric_value": numeric,
         "source_locator": locator, "missing_metadata": {"uncertainty": {"reason": unc_reason}},
         "review": review_obj(src_hash_id, method, how)}
    if qualifier:
        a["metric_qualifier"] = qualifier
    if unit_detail:
        a["unit_detail"] = unit_detail
    if raw is not None:
        a["raw_xml_value"] = raw
    if printed_cell is not None:
        a["printed_source_cell"] = printed_cell
    rid = f"{P}-result-{short}"
    rec("result", rid, f"{short} {metric}", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        a, srcs, links=[("evaluation", ev)])
    claims_rows.append([rid, src_hash_id, locator, printed, "result"])


# Drost Data S1 -------------------------------------------------------------
wb = rawxlsx.read(art["drost_s1"])
s3, s4 = wb["Table S3"], wb["Table S4"]


def expect(cells, ref, value):
    got = cells.get(ref)
    assert got == value, f"{ref}: expected {value!r}, got {got!r}"


expect(s3, "B2", "Table S3: AUROC and AUPRC for SpliceAI, Pangolin, SPiP and SQUIRLS performance")
expect(s3, "B4", "Entire Dataset"); expect(s3, "F4", "Stratified datasets")
for ref, v in (("B9", "Tool"), ("C9", "AUROC"), ("D9", "AUPRC"), ("F6", "Tool"), ("G6", "Dataset"), ("H6", "AUROC"), ("I6", "AUPRC"),
               ("G7", "CAGI6"), ("G12", "In House")):
    expect(s3, ref, v)
TOOLS = ["Pangolin", "SPiP", "SpliceAI", "Squirls"]
TOOL_KEY = {"Pangolin": "d_pangolin", "SPiP": "d_spip", "SpliceAI": "d_spliceai", "Squirls": "d_squirls"}
for i, t in enumerate(TOOLS):
    expect(s3, f"B{10 + i}", t); expect(s3, f"F{7 + i}", t); expect(s3, f"F{12 + i}", t)
expect(s4, "B2", "Table S4: Sensitivity, Specificity, Precision, F1, Positive and Negative Predictive Values for the SpliceAI, Pangolin, SPiP and SQUIRLS in silico splice prediction tools")
BLOCKS = {"merged": (4, "Entire Dataset", 6), "cagi6": (17, "CAGI6 dataset", 19), "inhouse": (30, "In House dataset", 32)}
S4COLS = [("C", "Sensitivity (Recall)", "recall", "column 'Sensitivity (Recall)'"),
          ("D", "Specificity", "specificity", None),
          ("E", "Precision", "precision", "column 'Precision'"),
          ("F", "F1", "f1-score", None),
          ("G", "Pos Pred Value", "precision", "column 'Pos Pred Value'"),
          ("H", "Neg Pred Value", "negative-predictive-value", None)]
ROWS4 = TOOLS + [f"AtLeast{n}" for n in range(1, 5)]
for key, (title_row, title, head) in BLOCKS.items():
    expect(s4, f"B{title_row}", title)
    expect(s4, f"B{head}", "Predictor")
    for col, label, _, _ in S4COLS:
        expect(s4, f"{col}{head}", label)
    for j, lab in enumerate(ROWS4):
        expect(s4, f"B{head + 1 + j + (1 if j >= 4 else 0)}", lab)

DATA_LABEL = {"merged": "243 scorable variants (in-house plus CAGI6)", "cagi6": "56 CAGI6 Splicing VUS variants", "inhouse": "in-house scorable variants (count not printed)"}
D_COMP = {
    "dataset_version": "Data S1 Table S2 variant set (as published)", "split": "No training split",
    "inputs": "Variant (GRCh37/38 coordinates as annotated by each tool); no patient RNA input to the predictors",
    "adaptation": "None; pretrained predictors with literature thresholds", "metric_implementation": "R: plotROC 2.3.1 (ROC), yardstick 1.2.0 (PR), caret 6.0.94 (binary statistics)",
    "aggregation": "Pooled over variants", "budget": None}
EV = {}
HOW_X = "Deterministic parse of the pinned XLSX cell XML (extract/extract_rna_splicing.py) with sheet title, block titles, column headers and row labels asserted; printed_value is the shortest round-trip decimal of the stored double, raw_xml_value keeps the stored text."
for key in BLOCKS:
    for cfgk in [TOOL_KEY[t] for t in TOOLS] + [f"d_al{n}" for n in range(1, 5)]:
        cfg = C[cfgk]
        origin = "author_reported" if cfgk.startswith("d_al") else "independent_paper"
        short = f"drost2025-{key}-{cfgk[2:].replace('_', '-')}"
        lims = ["Consensus rule devised and evaluated by the same authors on the same variants."] if origin == "author_reported" else None
        cname = next(r["name"] for r in records if r["id"] == cfg).replace(" (Drost et al.)", "")
        EV[(key, cfgk)] = evaluation(short, f"{cname} on {DATA_LABEL[key]}", cfg, PR[key],
                                     {"merged": D["merged"], "cagi6": D["cagi6"], "inhouse": D["inhouse"]}[key], DS, origin,
                                     dict(D_COMP, population=DATA_LABEL[key]),
                                     BLOCKS[key][1] + " block of Data S1 Table S4" + ("" if cfgk.startswith("d_al") else " and matching Table S3 rows"), FAC_DNA, lims)

# Table S3 (AUROC, AUPRC)
for i, t in enumerate(TOOLS):
    for key, col_auroc, col_auprc, row, block in (("merged", "C", "D", 10 + i, "'Entire Dataset'"),
                                                   ("cagi6", "H", "I", 7 + i, "'Stratified datasets', Dataset 'CAGI6'"),
                                                   ("inhouse", "H", "I", 12 + i, "'Stratified datasets', Dataset 'In House'")):
        ev = EV[(key, TOOL_KEY[t])]
        for col, metric in ((col_auroc, "auroc"), (col_auprc, "auprc")):
            raw = s3[f"{col}{row}"]
            v = shortest(raw)
            result(f"drost2025-{key}-{TOOL_KEY[t][2:]}-{metric}", ev, DS, S_DROST1, metric, "higher", "fraction", v, v,
                   "continuous score", f"Data S1 Table S3 {block}, cell {col}{row}; row {t}, column {metric.upper()}", HOW_X,
                   "deterministic-table-parse", raw=raw)

# Table S4 (thresholded)
for key, (title_row, title, head) in BLOCKS.items():
    for j, lab in enumerate(ROWS4):
        row = head + 1 + j + (1 if j >= 4 else 0)
        cfgk = TOOL_KEY[lab] if lab in TOOL_KEY else f"d_al{lab[-1]}"
        ev = EV[(key, cfgk)]
        for col, label, metric, colq in S4COLS:
            raw = s4[f"{col}{row}"]
            v = shortest(raw)
            q = ("binarised at each tool's literature threshold" if lab in TOOL_KEY else "at-least-N consensus of four thresholded tools")
            if colq:
                q += "; " + colq
            mshort = {"recall": "sensitivity", "precision": "precision" if label == "Precision" else "ppv"}.get(metric, metric)
            result(f"drost2025-{key}-{cfgk[2:].replace('_', '-')}-{mshort}", ev, DS, S_DROST1, metric, "higher", "fraction", v, v, q,
                   f"Data S1 Table S4 '{title}', cell {col}{row}; row {lab}, column {label}", HOW_X, "deterministic-table-parse", raw=raw)

# Segarra-Casas Table 2 -----------------------------------------------------
t = ET.parse(art["segarra"]).getroot()
tw = [x for x in t.iter("table-wrap") if x.get("id") == "acn370078-tbl-0002"][0]
assert txt(tw.find("caption")) == "Pathogenic splicing alterations identified by each splicing and expression tool."
trs = list(tw.iter("tr"))
head = [txt(c) for c in trs[0]]
assert head == ["Case no.", "Variant (cDNA)", "Splicing alteration", "FRASER |ΔPSI| > 0.1", "FRASER |ΔPSI| > 0.3", "FRASER2",
                "LeafcutterMD", "rMATS‐turbo", "Aberrant expression (OUTRIDER z‐score)"], head
body = trs[1:]
assert len(body) == 16
EXPECT_CASES = ["DMD1", "DMD2", "DMD3", "2*", "7*", "10", "22", "28", "37", "43*", "49", "61*", "63", "63", "69", "70"]
assert [txt(r[0]) for r in body] == EXPECT_CASES
SEG_COLS = [(3, "s_fraser01", "FRASER |ΔPSI| > 0.1"), (4, "s_fraser03", "FRASER |ΔPSI| > 0.3"), (5, "s_fraser2", "FRASER2"),
            (6, "s_leafcutter", "LeafcutterMD"), (7, "s_rmats", "rMATS‐turbo")]
S_COMP = {"dataset_version": "Segarra-Casas et al. muscle RNA-seq cohort (as published)", "split": "No split",
          "population": "16 known pathogenic splicing alterations in 15 cases; 98-sample muscle RNA-seq cohort",
          "inputs": "Muscle-biopsy total RNA-seq, HISAT2 alignment to GRCh37, neuromuscular-disease gene set", "adaptation": None,
          "metric_implementation": None, "aggregation": "Per event", "budget": None}
S_MISS = {"metric_implementation": {"reason": "unreported", "note": "Caller significance cutoffs beyond the printed |dPSI| thresholds are in File S1, not read"}}
HOW_T = "Deterministic parse of the pinned article XML table (extract/extract_rna_splicing.py) with caption, column headers and case labels asserted; printed text kept exactly, including Unicode minus and footnote text."
for col, ck, label in SEG_COLS:
    ev = evaluation(f"segarracasas2025-{ck[2:].replace('_', '-')}", f"{label} on 16 known pathogenic muscle splicing events", C[ck],
                    PR["muscle_splice"], D["muscle"], SG, "independent_paper", S_COMP, f"Table 2 column '{label}'", FAC_RNA, missing=S_MISS)
    for i, r in enumerate(body):
        cell = r[col]
        printed = txt(cell)
        bold = cell.find(".//bold") is not None
        case, var, alt = txt(r[0]), txt(r[1]), txt(r[2])
        qual = f"case {case}, {var}, {alt}"
        result(f"segarracasas2025-{ck[2:].replace('_', '-')}-event-{i + 1:02d}", ev, SG, S_SEG, "event-detected", "unknown", "unitless",
               printed, None, qual, f"Table 2 row {i + 1} (case {case}), column '{label}'", HOW_T, "deterministic-table-parse",
               unit_detail="Printed Yes or No per known event", printed_cell=("bold" if bold else "not bold"), unc_reason="inapplicable")
ev = evaluation("segarracasas2025-outrider", "OUTRIDER z-score at 16 known pathogenic muscle splicing events", C["s_outrider"], PR["muscle_expr"],
                D["muscle"], SG, "independent_paper", dict(S_COMP, inputs="StringTie gene counts from muscle-biopsy RNA-seq"),
                "Table 2 column 'Aberrant expression (OUTRIDER z-score)'", FAC_RNA)
for i, r in enumerate(body):
    cell = r[8]
    printed = txt(cell)
    num = printed.replace("−", "-")
    float(num)
    bold = cell.find(".//bold") is not None
    case, var, alt = txt(r[0]), txt(r[1]), txt(r[2])
    result(f"segarracasas2025-outrider-event-{i + 1:02d}", ev, SG, S_SEG, "z-score", "unknown", "unitless", printed, num,
           f"case {case}, {var}, {alt}", f"Table 2 row {i + 1} (case {case}), column 'Aberrant expression (OUTRIDER z-score)'", HOW_T,
           "deterministic-table-parse", unit_detail="Expression z-score of the affected gene; bold marks a correct outlier call (footnote)",
           printed_cell=("bold" if bold else "not bold"))

# Segers Table 2 ------------------------------------------------------------
t = ET.parse(art["segers"]).getroot()
tw = [x for x in t.iter("table-wrap") if x.get("id") == "Tab2"][0]
assert txt(tw.find("caption")) == "Detection of disease-related genes"
trs = list(tw.iter("tr"))
assert [txt(c) for c in trs[0]] == ["", "Aberrant expression", "Aberrant splicing"]
assert [txt(c) for c in trs[1]] == ["Sample: Gene", "saseR", "OutSingle", "OUTRIDER", "saseR", "FRASER 2.0"]
assert [txt(c) for c in trs[2]] == ["AUTO", "PCA", "junctions", "AUTO", "PCA"]
body = trs[3:]
EXPECT_ROWS = ["MUC1396: MGST1", "MUC1365: TIMMDC1", "MUC1344: TIMMDC1", "MUC1350: CLPP", "MUC1398: TAZ", "MUC1436: TANGO2", "MUC1410: TALDO1",
               "X76624: SFXN4", "MUC1395: COASY", "MUC1393: PANK2", "MUC1404: ALDH18A1", "MUC1361: MCOLN1"]
assert [txt(r[0]) for r in body] == EXPECT_ROWS
SEGERS_COLS = [(1, "g_saser_expr", "Aberrant expression: saseR", "expr"), (2, "g_outsingle", "Aberrant expression: OutSingle", "expr"),
               (3, "g_outrider_auto", "Aberrant expression: OUTRIDER AUTO", "expr"), (4, "g_outrider_pca", "Aberrant expression: OUTRIDER PCA", "expr"),
               (5, "g_saser_junc", "Aberrant splicing: saseR junctions", "splice"), (6, "g_fraser2_auto", "Aberrant splicing: FRASER 2.0 AUTO", "splice"),
               (7, "g_fraser2_pca", "Aberrant splicing: FRASER 2.0 PCA", "splice")]
G_COMP = {"dataset_version": "Kremer fibroblast RNA-seq count compendium (Zenodo release used by the FRASER paper)", "split": "No split",
          "population": "12 diagnosed patient samples with a reported disease gene, ranked within a 119-sample analysis",
          "adaptation": "Latent factors fitted on the same 119 samples", "metric_implementation": "Rank of the method's score for the disease gene within the patient sample",
          "aggregation": "Per patient", "budget": None}
for col, ck, label, part in SEGERS_COLS:
    origin = "author_reported" if ck.startswith("g_saser") else "independent_paper"
    inputs = ("Junction read counts (79,077 junctions after FRASER filtering)" if part == "splice" else "Gene read counts (14,379 genes after filtering)")
    ev = evaluation(f"segers2026-{ck[2:].replace('_', '-')}", f"{label} on 12 Kremer patients with known disease genes", C[ck],
                    PR["kremer_splice" if part == "splice" else "kremer_expr"], KREMER, SS, origin, dict(G_COMP, inputs=inputs),
                    f"Table 2 column '{label}'", FAC_RNA,
                    limitations=(["Developer evaluation of saseR."] if origin == "author_reported" else ["Run by the saseR authors, not the tool developers."]))
    for i, r in enumerate(body):
        printed = txt(r[col])
        int(printed)
        sample = txt(r[0])
        result(f"segers2026-{ck[2:].replace('_', '-')}-{sample.split(':')[0].lower()}-{i + 1:02d}", ev, SS, S_SASER, "known-gene-rank", "lower", "unitless",
               printed, printed, f"patient sample and gene {sample}", f"Table 2 row {i + 1} ('{sample}'), column '{label}'", HOW_T,
               "deterministic-table-parse", unit_detail="Rank among genes in the patient's sample; 1 is the top-ranked gene")

# ---------------------------------------------------------------- descriptive claims
def claim(short, subject, field, value, srcs, src_hash_id, locator):
    cid = f"{P}-claim-{short}"
    rec("claim", cid, f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.",
        {"field": field, "value": value, "source_locator": locator,
         "review": review_obj(src_hash_id, "transcription", "Hand transcription from the article XML text.")},
        srcs, links=[("subject", subject)])
    claims_rows.append([cid, src_hash_id, locator, value, "claim"])


claim("drost2025-alamut-selection", D["inhouse"], "selection_bias",
      "In most cases (87%, n = 176/202) variants were identified as potentially spliceogenic by a laboratory specialist using Alamut Visual Plus (>10% change in 2 of 4 predictions) before RNA analysis was requested.",
      DS, S_DROST, "Results 'RNA splicing analysis reclassifies 54% of VUS' paragraph 1")
claim("segarracasas2025-prose-detection-rates", PR["muscle_splice"], "reported_detection_rates",
      "Results: FRASER |dPSI| > 0.1 identified 81.26% (13/16) of events, FRASER2 68.7% (11/16) and LeafCutterMD 25%. Discussion: FRASER2 detects 66.6% of pathogenic events.",
      SG, S_SEG, "Results 'Aberrant Splicing Detection' paragraph 3; Discussion paragraph 6")
claim("segarracasas2025-leafcuttermd-intron-retention", C["s_leafcutter"], "design_limitation",
      "LeafCutterMD is not designed to identify intron retention events; one aberrant transcript was an intron retention in five of the 16 events (cases 28, 37, 61, 63 and 69).",
      SG, S_SEG, "Discussion paragraph 3")
claim("segers2026-kremer-junction-counts-only", PR["kremer_splice"], "allowed_information",
      "saseR-bins, saseR-ASpli, LeafcutterMD and SPOT could not be benchmarked on the Kremer dataset, as only junction read-counts are publicly available.",
      SS, S_SASER, "Results 'Detection of aberrant splicing' paragraph 3")

# ---------------------------------------------------------------- relevance judgements
CONSTR = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
          "Do not combine this mapping's evaluations with any other protocol's results; truth sets, inputs and metrics differ between sources."]


def judgement(short, proto, relevance, endpoint, rationale, limitations, cites, group, title, headline, stratum=None, order=None, reason=None):
    a = {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": relevance, "endpoint": endpoint, "rationale": rationale,
         "constraints": CONSTR, "limitations": limitations,
         "citation_locators": [{"source_id": s, "locator": loc} for s, loc in cites],
         "source_locator": "; ".join(f"{s}: {loc}" for s, loc in cites),
         "revision": 1, "reason": reason or "Recorded from the patient-RNA splicing use-case pass 2026-10-09 (data/omics/use-case-coverage-rna-splicing-20261009/).",
         "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        a["stratum_label"], a["stratum_order"] = stratum, order
    pname = next(r["name"] for r in records if r["id"] == proto)
    rec("claim", f"use-case-mapping-rna-splicing-20261009-{short}",
        f'Relevance of {pname} to "Select a patient-RNA splicing-variant validation workflow"', rationale, a,
        sorted({s for s, _ in cites}), links=[("subject", UC)])
    return proto


J = []
DR_REASON = ("Recorded from the patient-RNA splicing use-case pass 2026-10-09. Held as draft while the article source carries an evidence concern "
             "(Results prose prints SQUIRLS AUPRC 0.888 against 0.881 in Data S1 Table S3).")
DR_TITLE = "DNA splice predictors against patient-RNA or exon-trapping results (Drost et al. 2025)"
for key, short, stratum, order, endpoint in (
        ("merged", "drost2025-merged", "All 243 scorable variants", 1,
         "AUROC and AUPRC from continuous scores, and sensitivity, specificity, precision, F1, PPV and NPV at literature thresholds, for SpliceAI, Pangolin, SPiP, SQUIRLS and at-least-N consensus rules on 243 clinically ascertained variants with experimental splicing results"),
        ("inhouse", "drost2025-inhouse", "In-house diagnostic variants", 2,
         "The same metrics on the in-house diagnostic variants tested in patient RNA or exon trapping"),
        ("cagi6", "drost2025-cagi6", "CAGI6 Splicing VUS variants", 3,
         "The same metrics on the 56 CAGI6 Splicing VUS variants")):
    J.append(judgement(short, PR[key], "direct", endpoint,
                       "Classification of variant-level splicing effect against results in patient RNA (or exon trapping where tissue RNA was unusable) directly measures how well DNA-based predictors identify splice-altering variants before follow-up; it does not measure pathogenicity or the RNA-seq calling step.",
                       DROST_LIM + (["Small stratum: 56 variants; Table S4 prints identical values for Pangolin, SPiP and SpliceAI in this block."] if key == "cagi6" else []),
                       [(S_DROST1, BLOCKS[key][1] + " block of Table S4 and matching Table S3 cells"), (S_DROST, "Methods 'In silico splice predictions'; Results 'Additional splicing prediction tools can help predict variant effect on splicing'")],
                       "drost2025-rna-validated-variants", DR_TITLE, "auroc", stratum, order, DR_REASON))
SEG_TITLE = "RNA-seq callers on 16 known pathogenic splicing events in muscle (Segarra-Casas et al. 2025)"
J.append(judgement("segarracasas2025-splicing", PR["muscle_splice"], "direct",
                   "Per-event detection (Yes/No) of 16 known pathogenic splicing alterations in clinical muscle RNA-seq by FRASER (|dPSI| > 0.1 and > 0.3), FRASER2, LeafCutterMD and rMATS-turbo",
                   "Recovery of established pathogenic splicing events in patient tissue RNA-seq, with several callers on the same samples, directly informs the choice of RNA calling step; it is known-event recovery, not diagnostic yield.",
                   ["Independent clinical comparison, 16 events in one tissue (skeletal muscle); no confidence intervals.",
                    "Events were established partly with the same callers; recall is on events at least one method revealed.",
                    "Per-run sample count not printed in Table 2; FRASER2 case 2 detected only with the full cohort.",
                    "No false-positive or workload counts in the table (Figure 2A only)."],
                   [(S_SEG, "Table 2; Results 'Aberrant Splicing Detection'; Methods 'Aberrant Splicing'")],
                   "segarracasas2025-muscle", SEG_TITLE, "event-detected", "Aberrant-splicing callers", 1))
J.append(judgement("segarracasas2025-outrider", PR["muscle_expr"], "proxy",
                   "OUTRIDER expression z-score of the affected gene at each of the 16 known pathogenic splicing events, with bold marking an outlier call",
                   "Aberrant expression of the affected gene is indirect evidence for a splice-altering variant (for example through nonsense-mediated decay); it does not detect the splicing event itself.",
                   ["Single configuration, no comparator for expression.", "In-frame events are not expected to change expression.",
                    "Outlier threshold not printed in the table."],
                   [(S_SEG, "Table 2 column 'Aberrant expression (OUTRIDER z-score)'; Methods 'Gene Expression'")],
                   "segarracasas2025-muscle", SEG_TITLE, "z-score", "Aberrant expression (OUTRIDER)", 2))
SAS_TITLE = "Rank of known disease genes in 12 Kremer fibroblast samples (Segers et al. 2026)"
J.append(judgement("segers2026-kremer-splicing", PR["kremer_splice"], "direct",
                   "Rank of 12 reported disease genes within the patient sample for saseR-junctions, FRASER 2.0 autoencoder and FRASER 2.0 PCA on the 119-sample Kremer fibroblast cohort",
                   "Prioritisation of known disease genes by aberrant-splicing callers in patient fibroblast RNA bears directly on choosing the RNA calling step; the cohort is the one behind the existing FRASER judgement.",
                   ["Developer comparison (saseR authors ran FRASER 2.0); no uncertainty.",
                    "12 genes include expression and mono-allelic-expression cases, so not all are splicing defects.",
                    "Retrospective genes reported in earlier analyses of the same cohort."],
                   [(S_SASER, "Table 2 'Aberrant splicing' columns; Results 'Case study: Kremer dataset'")],
                   "segers2026-kremer", SAS_TITLE, "known-gene-rank", "Aberrant splicing", 1))
J.append(judgement("segers2026-kremer-expression", PR["kremer_expr"], "proxy",
                   "Rank of the same 12 disease genes for saseR, OutSingle, OUTRIDER autoencoder and OUTRIDER PCA aberrant-expression scores",
                   "Expression outlier ranking is indirect evidence for splice-altering variants; it is useful alongside the splicing columns of the same table but does not identify splicing events.",
                   ["Developer comparison (saseR authors ran OUTRIDER and OutSingle); no uncertainty.",
                    "Same 12 genes and cohort as the splicing stratum."],
                   [(S_SASER, "Table 2 'Aberrant expression' columns; Results 'Case study: Kremer dataset'")],
                   "segers2026-kremer", SAS_TITLE, "known-gene-rank", "Aberrant expression", 2))

# ---------------------------------------------------------------- write
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids))
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
claims_rows.sort()
with open(os.path.join(OUT, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
from collections import Counter
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True))
print("judged protocols:", J)
