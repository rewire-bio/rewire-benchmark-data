"""Deterministic extraction for the regulatory variant and gene follow-up use-case pass, 2026-10-09.

Usage: python3 -I extract_regulatory_variant.py <download-dir> <batch-dir>

<download-dir> layout:
  PMC13471189/fulltext.xml, PMC13471189/supp.zip, PMC13471189/supp/41586_2026_10781_MOESM3_ESM.zip and
  PMC13471189/s3/2023-11-20318B-s3/Supplementary_Table_3.xlsx   (Gschwind et al. 2026, Nature)
  PMC12562713/fulltext.xml                                        (Manzo et al. 2025, Genes)
  PMC12261763/fulltext.xml                                        (Tang et al. 2025, Genome Biology)

Writes batch.jsonl and claims.csv. Extracts every cell of Supplementary Table 3 sheet
'Held-out benchmarks' (Gschwind), Table 1 (Manzo) and Table 1 (Tang), with labels asserted.
"""
import csv, hashlib, json, os, re, sys, xml.etree.ElementTree as ET
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

DL, OUT = sys.argv[1], sys.argv[2]
P = "regulatory-variant-20261009"
UC = "use-case-regulatory-variant-gene-follow-up"
UC_NAME = "Select regulatory variants and genes for functional follow-up"
DATE = "2026-10-09"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
FAC = {"areas": ["dna-genomes"], "contexts": ["research"]}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def txt(e):
    return " ".join("".join(e.itertext()).split())


def shortest(raw):
    s = repr(float(raw))
    return format(float(raw), "f") if ("e" in s or "E" in s) else s


records, claims_rows = [], []


def rec(kind, id_, name, description, attributes, source_ids, links=(), facets=None):
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
                    "facets": facets if facets is not None else {}, "source_ids": list(source_ids),
                    "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attributes})
    return id_


art = {"gs": os.path.join(DL, "PMC13471189", "fulltext.xml"),
       "gs_t3": os.path.join(DL, "PMC13471189", "s3", "2023-11-20318B-s3", "Supplementary_Table_3.xlsx"),
       "gs_moesm3": os.path.join(DL, "PMC13471189", "supp", "41586_2026_10781_MOESM3_ESM.zip"),
       "gs_zip": os.path.join(DL, "PMC13471189", "supp.zip"),
       "mz": os.path.join(DL, "PMC12562713", "fulltext.xml"),
       "tk": os.path.join(DL, "PMC12261763", "fulltext.xml")}
H = {k: sha(v) for k, v in art.items()}
S_GS, S_GS3, S_MZ, S_TK = (f"{P}-source-gschwind2026", f"{P}-source-gschwind2026-table-s3", f"{P}-source-manzo2025", f"{P}-source-tang2025")
URL = {S_GS: EPMC + "PMC13471189/fullTextXML", S_GS3: EPMC + "PMC13471189/supplementaryFiles",
       S_MZ: EPMC + "PMC12562713/fullTextXML", S_TK: EPMC + "PMC12261763/fullTextXML"}
SHA = {S_GS: H["gs"], S_GS3: H["gs_t3"], S_MZ: H["mz"], S_TK: H["tk"]}


def source(sid, name, desc, a):
    base = {"artifact_url": URL[sid], "artifact_sha256": SHA[sid], "publication_status": "peer_reviewed"}
    rec("source", sid, name, desc, dict(base, **a), [], facets=FAC)


source(S_GS, "An encyclopedia of human enhancer-gene regulatory interactions", "Primary source retrieved and hashed for the regulatory variant follow-up pass.",
       {"url": "https://doi.org/10.1038/s41586-026-10781-4", "doi": "10.1038/s41586-026-10781-4", "retrieved_at": "2026-10-09T21:03:18Z",
        "version": "Nature 657(8130):179, published online 2026-07-15; PMC13471189 full-text XML", "licence": "CC-BY-4.0", "media_type": "application/xml"})
source(S_GS3, "Gschwind et al. 2026, Supplementary Table 3", "Workbook of predictor performance on CRISPR enhancer-gene benchmarks.",
       {"url": "https://doi.org/10.1038/s41586-026-10781-4", "doi": "10.1038/s41586-026-10781-4", "retrieved_at": "2026-10-09T21:04:46Z",
        "version": "Supplementary_Table_3.xlsx in 41586_2026_10781_MOESM3_ESM.zip (folder 2023-11-20318B-s3) inside the Europe PMC supplementaryFiles zip",
        "licence": "CC-BY-4.0", "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "hash_scope": f"SHA-256 of the xlsx member. MOESM3 zip SHA-256 {H['gs_moesm3']}; outer supplementaryFiles zip SHA-256 {H['gs_zip']} (assembled per request)."})
source(S_MZ, "Comparative Analysis of Deep Learning Models for Predicting Causative Regulatory Variants", "Primary source retrieved and hashed for the regulatory variant follow-up pass.",
       {"url": "https://doi.org/10.3390/genes16101223", "doi": "10.3390/genes16101223", "retrieved_at": "2026-10-09T21:04:27Z",
        "version": "Genes 16(10):1223, published 2025-10-15; PMC12562713 full-text XML", "licence": "CC-BY-4.0", "media_type": "application/xml"})
source(S_TK, "Evaluating the representational power of pre-trained DNA language models for regulatory genomics", "Primary source retrieved and hashed for the regulatory variant follow-up pass.",
       {"url": "https://doi.org/10.1186/s13059-025-03674-8", "doi": "10.1186/s13059-025-03674-8", "retrieved_at": "2026-10-09T21:04:28Z",
        "version": "Genome Biology 26:203, published 2025-07-14; PMC12261763 full-text XML", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml"})

# ---------------------------------------------------------------- methods (new only; existing reused below)
M = {"abc": "ucc-research-method-mprabc-abc", "re2g": "ucc-research-method-mprabc-re2g", "dnabert2": "catalog-model-dnabert-2",
     "ntv2": "catalog-model-nt-v2", "nt": "discovery-model-nucleotide-transformer", "geneformer": "catalog-model-geneformer",
     "chrombpnet": "discovery-model-chrombpnet"}
SML, FM, CP = "supervised_machine_learning", "foundation_model", "conventional_pipeline"


def method(key, name, desc, srcs, locator, mtype):
    M[key] = rec("method", f"{P}-method-{key}", name, desc,
                 {"reported_name": name, "entity_level": "method", "source_locator": locator,
                  "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
                 srcs, facets=dict(FAC, method_types=[mtype]))


GL = "Gschwind et al. Results 'Systematic benchmarking of ENCODE-rE2G' and Supplementary Table 1"
method("epiraction", "EPIraction", "Published enhancer-gene prediction model.", [S_GS], GL, SML)
method("epimap", "EpiMap enhancer-gene links", "Published enhancer-gene linking predictions from the EpiMap resource.", [S_GS], GL, SML)
method("distance-to-tss", "Distance to TSS baseline", "Ranks element-gene pairs by distance from the element to the gene's TSS.", [S_GS], GL, CP)
method("ep-dnase-correlation", "Element-promoter DNase-seq correlation baseline", "Correlation of DNase-seq signal at the element and the promoter across cell types.", [S_GS], GL, CP)
ML = "Manzo et al. Table 2 and Table 3"
TL = "Tang et al. Table 1 and Methods"
method("gena-lm", "GENA-LM", "Transformer DNA language model family (BERT and BigBird variants).", [S_MZ], ML, FM)
method("hyenadna", "HyenaDNA", "Long-context Hyena-operator DNA language model.", [S_MZ, S_TK], "; ".join([ML, TL]), FM)
method("caduceus", "Caduceus", "Bidirectional reverse-complement-equivariant Mamba DNA language model.", [S_MZ], ML, FM)
method("trednet", "TREDNet", "Two-phase CNN enhancer and variant-effect model.", [S_MZ], ML, SML)
method("sei", "Sei", "CNN sequence model of chromatin profiles and sequence classes.", [S_MZ, S_TK], "; ".join([ML, TL]), SML)
method("enformer", "Enformer", "Transformer-convolution model of genomic tracks from long input sequence.", [S_MZ, S_TK], "; ".join([ML, TL]), SML)
method("borzoi", "Borzoi", "Model predicting RNA-seq coverage and other tracks from long DNA sequence.", [S_MZ], ML, SML)
method("gpn", "GPN", "Genomic pre-trained network (masked DNA language model).", [S_TK], TL, FM)
method("lentimpra-cnn-probe", "CNN on lentiMPRA, trained by Tang et al.", "CNN trained on lentiMPRA activity from one-hot sequence or from frozen pretrained embeddings.", [S_TK], TL, SML)
method("residualbind", "ResidualBind", "Residual CNN architecture trained on lentiMPRA by Tang et al.", [S_TK], TL, SML)
method("mprann", "MPRAnn", "CNN architecture for MPRA activity trained on lentiMPRA by Tang et al.", [S_TK], TL, SML)

# ---------------------------------------------------------------- configurations
C = {}


def config(key, name, of, srcs, mtype, version=None, vnote="Version not printed", params=None, locator=None, limitations=None):
    a = {"reported_name": name, "foundation_model_eligible": mtype == FM}
    if version:
        a["version"] = version
    else:
        a["missing_metadata"] = {"version": {"reason": "unreported", "note": vnote}}
    for k, v in (("parameters", params), ("source_locator", locator), ("limitations", limitations)):
        if v:
            a[k] = v
    C[key] = rec("configuration", f"{P}-config-{key}", name, f"{name} as evaluated in the cited comparison.", a, srcs,
                 links=[("configuration_of", of)], facets=dict(FAC, method_types=[mtype]))


GSD = [S_GS, S_GS3]
GS_PRED = {"ABC_A=DNase, C=Average ENCODE Hi-C": ("abc-dnase-avg-hic", M["abc"], SML, "Activity from DNase-seq, contact from average ENCODE Hi-C"),
           "ENCODE-rE2G": ("encode-re2g", M["re2g"], SML, "DNase-only ENCODE-rE2G logistic regression model"),
           "EPIraction": ("epiraction", M["epiraction"], SML, None),
           "EpiMap": ("epimap", M["epimap"], SML, None),
           "Distance to TSS": ("distance-to-tss", M["distance-to-tss"], CP, None),
           "Correlation_E-P DNase-seq signal": ("ep-dnase-correlation", M["ep-dnase-correlation"], CP, None)}
for label, (short, of, mt, params) in GS_PRED.items():
    config(f"gschwind2026-{short}", f"{label} (Gschwind et al. 2026)", of, GSD, mt, params=params,
           vnote="Predictor version not printed in Supplementary Table 3; parameters are in Supplementary Table 1 (not read)",
           locator=f"Supplementary Table 3 'Held-out benchmarks', predictor '{label}'")

MZ_ROWS = ["DNABERT-2", "NT v2-50m-ms", "NT v2-100m-ms", "NT v2-250m-ms", "NT v2 500m-ms", "NT 500m1000g", "NT 500m-h-ref", "NT 2.5b-1000g", "NT 2.5b-m-s",
           "Geneformer", "Gena LM-base", "Gena LM large", "Gena LM b-multi", "Gena LM bigbird", "Hyenadna 32 k", "Hyenadna 160 k", "Hyenadna 450 k",
           "Hyenadna 1 mf", "Caduceus", "ChromBPNet", "TREDNet", "SEI", "Enformer", "Borzoi"]
FT = "Fine-tuned per cell line for enhancer versus control classification on 1 kb sequences (Table 2); variant effect is the log2 ratio of alternative to reference scores"
INF = "Inference only on 1 kb sequences (Table 2); variant effect is the log2 ratio of alternative to reference scores"


def mz_family(row):
    if row == "DNABERT-2": return M["dnabert2"], FM, FT
    if row.startswith("NT v2"): return M["ntv2"], FM, FT
    if row.startswith("NT "): return M["nt"], FM, FT
    if row == "Geneformer": return M["geneformer"], FM, FT + "; Geneformer was trained on single-cell transcriptomes and adapted to DNA tokens by the authors"
    if row.startswith("Gena"): return M["gena-lm"], FM, FT
    if row.startswith("Hyenadna"): return M["hyenadna"], FM, INF + "; inputs padded to 32,768 tokens"
    if row == "Caduceus": return M["caduceus"], FM, "PS version with an appended classification layer (Table 2)"
    if row == "ChromBPNet": return M["chrombpnet"], SML, INF
    if row == "TREDNet": return M["trednet"], SML, INF
    if row == "SEI": return M["sei"], SML, INF
    if row == "Enformer": return M["enformer"], SML, INF + "; input truncated to 1 kb from the model's long context"
    if row == "Borzoi": return M["borzoi"], SML, INF + "; applied to 1 kb input"


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


for row in MZ_ROWS:
    of, mt, params = mz_family(row)
    config(f"manzo2025-{slug(row)}", f"{row} (Manzo et al. 2025)", of, [S_MZ], mt, version=f"{row} (as printed)", params=params,
           locator=f"Table 1 row '{row}'; Table 2", limitations=(["Long-context model evaluated on 1 kb input."] if row in ("Enformer", "Borzoi") else None))

TK_ROWS = [("Self-supervised pre-training", "NT (2B51000G)"), ("Self-supervised pre-training", "NT (2B5Species)"), ("Self-supervised pre-training", "NT (500MHuman)"),
           ("Self-supervised pre-training", "NT (500M1000G)"), ("Self-supervised pre-training", "GPN (human)"), ("Self-supervised pre-training", "HyenaDNA"),
           ("LentiMPRA-embedding", "CNN-GPN"), ("LentiMPRA-embedding", "CNN-NT"), ("LentiMPRA-embedding", "CNN-SEI"),
           ("LentiMPRA-one-hot", "CNN"), ("LentiMPRA-one-hot", "Residualbind"), ("LentiMPRA-one-hot", "MPRAnn"),
           ("Supervised one-hot", "SEI"), ("Supervised one-hot", "Enformer (DNase)")]
TK_FAM = {"NT (2B51000G)": (M["nt"], FM), "NT (2B5Species)": (M["nt"], FM), "NT (500MHuman)": (M["nt"], FM), "NT (500M1000G)": (M["nt"], FM),
          "GPN (human)": (M["gpn"], FM), "HyenaDNA": (M["hyenadna"], FM), "CNN-GPN": (M["lentimpra-cnn-probe"], SML), "CNN-NT": (M["lentimpra-cnn-probe"], SML),
          "CNN-SEI": (M["lentimpra-cnn-probe"], SML), "CNN": (M["lentimpra-cnn-probe"], SML), "Residualbind": (M["residualbind"], SML),
          "MPRAnn": (M["mprann"], SML), "SEI": (M["sei"], SML), "Enformer (DNase)": (M["enformer"], SML)}
TK_PARAMS = {"Self-supervised pre-training": "Zero-shot: cosine similarity of embeddings for mutant and wild-type sequence (NT, HyenaDNA) or log2 ratio of masked-nucleotide predictions (GPN)",
             "LentiMPRA-embedding": "CNN trained by the authors on lentiMPRA activity using frozen embeddings of the named model",
             "LentiMPRA-one-hot": "Trained by the authors on lentiMPRA activity from one-hot sequence",
             "Supervised one-hot": "Published supervised model on one-hot sequence"}
TK_KEY = {}
for task, model in TK_ROWS:
    of, mt = TK_FAM[model]
    key = f"tang2025-{slug(task)}-{slug(model)}"
    TK_KEY[(task, model)] = key
    config(key, f"{model}, {task} (Tang et al. 2025)", of, [S_TK], mt, version=f"{model} (as printed)", params=TK_PARAMS[task] + "; 230 nt sequences centred on each CRE",
           locator=f"Table 1 row '{task}' / '{model}'; Methods 'CAGI dataset'")

# ---------------------------------------------------------------- datasets and protocols
D, PR = {}, {}
D["gs_heldout"] = rec("dataset", f"{P}-data-gschwind2026-heldout-crispr", "Held-out CRISPR enhancer-gene pairs in five cell types (Gschwind et al. 2026)",
                      "Eight CRISPR perturbation screens (Perturb-seq, DC-TAP-seq, CRISPRi-FlowFISH) in K562, GM12878, HCT116, WTC11 and Jurkat, excluding pairs in the training data.",
                      {"version": "As published (Methods 'Creating the combined held-out CRISPR dataset')", "total": 4378, "positives": 190,
                       "population": "4,378 element-gene pairs, 190 positives (157.39 weighted); elements overlapping promoters or the target gene body removed; positives without H3K27ac removed; negatives filtered for power",
                       "split": "Held out from ENCODE-rE2G training", "source_locator": "Figure 2 legend (panel d); Methods 'Creating the combined held-out CRISPR dataset'"},
                      GSD, facets=FAC)
K562 = "ucc-research-data-mprabc-k562-crispri"
GS_PROTO = ("Overlap CRISPR-tested elements with each predictor's elements (matched by gene symbol; sum or max aggregation per Supplementary Table 1; unmatched pairs get the minimum score). "
            "Weighted precision-recall (yardstick 1.2.0), each pair weighted by its estimated probability of a direct cis-regulatory effect; weighted AUPRC, and weighted precision and recall at the predictor threshold, "
            "with 95% bootstrap intervals (10,000 iterations).")
GS_LIM = ["Developer comparison: ENCODE-rE2G and ABC come from the authors' group; other predictors and baselines were run or rebuilt by the authors.",
          "Whole-element CRISPRi perturbation, not allele editing; a regulatory link does not establish a causal disease role.",
          "Weighting depends on the authors' model of direct effects (Supplementary Methods 22).",
          "The threshold behind the 'precision at threshold' and 'recall at threshold' rows is not restated in the sheet (the training sheet sets thresholds at 70% recall)."]
PR["gs_heldout"] = rec("protocol", f"{P}-protocol-gschwind2026-heldout-weighted", "Held-out CRISPR enhancer-gene benchmark, weighted metrics, five cell types (Gschwind et al. 2026 Supplementary Table 3)",
                       "Enhancer-gene link prediction against CRISPR perturbation outcomes outside the training data.",
                       {"protocol": GS_PROTO, "version": "Supplementary Table 3 sheet 'Held-out benchmarks', Dataset 'Held-out'", "limitations": GS_LIM,
                        "source_locator": "Supplementary Table 3 'Held-out benchmarks' rows 2-19; Methods 'CRISPR benchmark'"},
                       GSD, links=[("uses_data", D["gs_heldout"])], facets=FAC)
PR["gs_k562"] = rec("protocol", f"{P}-protocol-gschwind2026-k562-training-weighted", "Combined K562 CRISPR training pairs, weighted metrics (Gschwind et al. 2026 Supplementary Table 3)",
                    "Enhancer-gene link prediction on the combined K562 CRISPR data used to train ENCODE-rE2G, with direct-effect weighting.",
                    {"protocol": GS_PROTO, "version": "Supplementary Table 3 sheet 'Held-out benchmarks', Dataset 'Combined K562 (training)'",
                     "limitations": GS_LIM + ["ENCODE-rE2G was trained on these pairs, so its values here are in-sample.",
                                              "Same 10,356 pairs as the existing K562 mapping's dataset; the weighting differs, so do not pool with that protocol."],
                     "source_locator": "Supplementary Table 3 'Held-out benchmarks' rows 20-37"},
                    GSD, links=[("uses_data", K562)], facets=FAC)

MZ_CELLS = [("K562", "K562 (19,321 SNPs)", 19321, "SuRE raQTLs (Dataset 1) and MPRA variants (Dataset 4)"),
            ("HepG2", "HepG2 (16,255 SNPs)", 16255, "SuRE raQTLs (Dataset 2), SORT1 luciferase saturation (Dataset 3) and eQTL-LD MPRA (Dataset 5)"),
            ("NPC", "NPC (14,042 SNPs)", 14042, "lentiMPRA of human-derived variants (Dataset 6)"),
            ("HeLa", "Hela (5241 SNPs)", 5241, "Coding-exon MPRA of SORL1, TRAF3IP2 and PPARG exons (Datasets 7-9)")]
MZ_LIM = ["Reporter (SuRE, MPRA, luciferase) activity, not endogenous regulation.",
          "TREDNet was developed by the same group (Ovcharenko lab).",
          "Transformers were fine-tuned for enhancer classification per cell line; CNNs and long-context models were used for inference on 1 kb input, so models were not adapted equally.",
          "Standard errors in brackets are not defined further in the caption."]
for short, label, n, desc in MZ_CELLS:
    D[f"mz_{short}"] = rec("dataset", f"{P}-data-manzo2025-{short.lower()}", f"{short} regulatory variant reporter data (Manzo et al. 2025)", desc,
                           {"version": "Manzo et al. Table 4 (as published)", "variants": n, "population": f"{n} SNPs in {short} per the Table 1 header; {desc}",
                            "split": "Evaluation of variant effects; no variant-level training for CNNs", "source_locator": "Table 1 header; Table 4"}, [S_MZ], facets=FAC)
    PR[f"mz_{short}"] = rec("protocol", f"{P}-protocol-manzo2025-{short.lower()}-pearson", f"Allelic reporter effect correlation in {short} (Manzo et al. 2025 Table 1)",
                            "Pearson correlation between predicted and measured log2 fold-change of variant effects in reporter assays.",
                            {"protocol": "Score 1 kb reference and alternative sequences centred on each SNP; correlate the predicted log2 ratio with the experimental log2 fold-change; standard error in brackets.",
                             "version": "Table 1", "source_locator": f"Table 1 column '{label}'; Results 2.1; Methods 4.1", "limitations": MZ_LIM},
                            [S_MZ], links=[("uses_data", D[f"mz_{short}"])], facets=FAC)
D["tk"] = rec("dataset", f"{P}-data-tang2025-cagi5-saturation-mpra", "CAGI5 saturation mutagenesis MPRA, four CREs (as used by Tang et al. 2025)",
              "Saturation mutagenesis MPRA of regulatory elements from the CAGI5 regulation challenge; HepG2 (LDLR printed as 'LDLT', SORT1, F9) and K562 (PKLR).",
              {"version": "CAGI5 challenge data (as used)", "population": "Single-nucleotide variants in 230 nt windows centred on four CREs",
               "split": "Zero-shot test; not used for training", "source_locator": "Methods 'CAGI dataset'"}, [S_TK], facets=FAC)
TK_LIM = ["Reporter (MPRA) activity in an episomal construct, not endogenous regulation.",
          "Very small: one CRE in K562 and the average of three CREs in HepG2.",
          "lentiMPRA-trained CNNs, ResidualBind and MPRAnn were trained by the same authors; other models are published.",
          "No uncertainty printed."]
for cell, desc in (("HepG2", "average Pearson r over three CREs (LDLR, SORT1, F9)"), ("K562", "Pearson r for one CRE (PKLR)")):
    PR[f"tk_{cell}"] = rec("protocol", f"{P}-protocol-tang2025-cagi5-{cell.lower()}", f"CAGI5 saturation MPRA variant effect correlation, {cell} (Tang et al. 2025 Table 1)",
                           f"Pearson correlation between predicted and MPRA-measured single-nucleotide variant effects; {desc}.",
                           {"protocol": "Zero-shot or transfer variant effect scores compared with experimental saturation mutagenesis effect sizes per CRE by Pearson correlation.",
                            "version": "Table 1", "source_locator": f"Table 1 column '{cell}' and footnote; Methods 'CAGI dataset'", "limitations": TK_LIM},
                           [S_TK], links=[("uses_data", D["tk"])], facets=FAC)

# ---------------------------------------------------------------- evaluations and results
def evaluation(short, name, cfg, proto, data, srcs, origin, comparison, locator, limitations=None):
    a = {"origin": origin, "protocol": proto, "version": "Primary source as retrieved 2026-10-09", "comparison": dict(comparison, protocol_id=proto), "source_locator": locator}
    if limitations:
        a["limitations"] = limitations
    return rec("evaluation", f"{P}-eval-{short}", name, "Published comparison; transcribed, not reproduced.", a, srcs,
               links=[("system", cfg), ("assessment", proto), ("data", data)], facets=FAC)


def result(short, ev, srcs, src, metric, printed, numeric, qualifier, locator, how, method, unit="fraction", uncertainty=None, raw=None):
    a = {"metric": metric, "metric_direction": "higher", "unit": unit, "printed_value": printed, "numeric_value": numeric, "source_locator": locator,
         "review": {"method": [method], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
                    "date": DATE, "artifact_sha256": SHA[src], "retrieval_url": URL[src], "note": how + " Pending independent review."}}
    if uncertainty:
        a["uncertainty"] = uncertainty
    else:
        a["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
    if qualifier:
        a["metric_qualifier"] = qualifier
    if raw is not None:
        a["raw_xml_value"] = raw
    rid = f"{P}-result-{short}"
    rec("result", rid, f"{short} {metric}", "Reported measurement transcribed from the pinned source. Not independently reproduced.", a, srcs, links=[("evaluation", ev)])
    claims_rows.append([rid, src, locator, printed, "result"])


# Gschwind sheet
sh = rawxlsx.read(art["gs_t3"])["Held-out benchmarks"]
assert [sh[f"{c}1"] for c in "ABCDEF"] == ["Dataset", "Predictor", "Performance metric", "Performance", "Lower CI", "Upper CI"]
METRIC = {"Weighted AUPRC": ("auprc", "weighted by estimated probability of a direct cis-effect", "auprc"),
          "Weighted precision at threshold": ("precision", "weighted; at predictor threshold", "precision"),
          "Weighted recall at threshold": ("recall", "weighted; at predictor threshold", "recall")}
HOW_X = "Deterministic parse of the pinned XLSX cell XML (extract/extract_regulatory_variant.py) with header row, dataset, predictor and metric labels asserted; printed_value is the shortest round-trip decimal of the stored double, raw_xml_value keeps the stored text."
GS_EV = {}
rows = sorted({int(re.sub("[A-Z]", "", k)) for k in sh} - {1})
assert rows == list(range(2, 38))
for r in rows:
    ds, pred, met = sh[f"A{r}"], sh[f"B{r}"], sh[f"C{r}"]
    assert ds in ("Held-out", "Combined K562 (training)") and pred in GS_PRED and met in METRIC, (r, ds, pred, met)
    pk = "gs_heldout" if ds == "Held-out" else "gs_k562"
    if (pk, pred) not in GS_EV:
        short = GS_PRED[pred][0]
        origin = "author_reported" if pred in ("ENCODE-rE2G", "ABC_A=DNase, C=Average ENCODE Hi-C", "Distance to TSS", "Correlation_E-P DNase-seq signal") else "independent_paper"
        GS_EV[(pk, pred)] = evaluation(f"gschwind2026-{'heldout' if pk == 'gs_heldout' else 'k562-training'}-{short}",
                                       f"{pred} on {'held-out CRISPR pairs, five cell types' if pk == 'gs_heldout' else 'combined K562 CRISPR training pairs'}",
                                       C[f"gschwind2026-{short}"], PR[pk], D["gs_heldout"] if pk == "gs_heldout" else K562, GSD, origin,
                                       {"dataset_version": "As published", "split": "Held out from training" if pk == "gs_heldout" else "ENCODE-rE2G training data",
                                        "population": "4,378 pairs, 190 positives" if pk == "gs_heldout" else "10,356 pairs, 471 positives",
                                        "inputs": "Predictor's genome-wide element-gene scores in the matching cell type", "adaptation": None,
                                        "metric_implementation": "yardstick 1.2.0 weighted precision-recall; boot 1.3-28.1", "aggregation": "Pooled over pairs, weighted", "budget": None},
                                       f"Supplementary Table 3 'Held-out benchmarks', Dataset '{ds}', Predictor '{pred}'",
                                       limitations=(["Developer of the predictor is an author of the comparison."] if origin == "author_reported" else None))
    metric, q, ms = METRIC[met]
    v, lo, hi = shortest(sh[f"D{r}"]), shortest(sh[f"E{r}"]), shortest(sh[f"F{r}"])
    result(f"gschwind2026-{'heldout' if pk == 'gs_heldout' else 'k562-training'}-{GS_PRED[pred][0]}-{ms}", GS_EV[(pk, pred)], GSD, S_GS3, metric, v, v, q,
           f"Supplementary Table 3 'Held-out benchmarks', row {r} (D{r}:F{r}); Dataset '{ds}', Predictor '{pred}', metric '{met}'", HOW_X, "deterministic-table-parse",
           uncertainty={"type": "confidence_interval", "printed": f"{lo} to {hi} (Lower CI, Upper CI columns)", "lower": lo, "upper": hi, "level": 0.95,
                        "method": "bootstrap", "resamples": 10000, "source_column": "Lower CI; Upper CI"}, raw=sh[f"D{r}"])

# Manzo Table 1
t = ET.parse(art["mz"]).getroot()
tw = [x for x in t.iter("table-wrap") if x.get("id") == "genes-16-01223-t001"][0]
assert txt(tw.find("caption")).startswith("Pearson correlation coefficient for various deep learning models across four cell lines")
trs = list(tw.iter("tr"))
assert [txt(c) for c in trs[1]] == ["Models"] + [c[1] for c in MZ_CELLS]
assert [txt(r[0]) for r in trs[2:]] == MZ_ROWS
HOW_T = "Deterministic parse of the pinned article XML table (extract/extract_regulatory_variant.py) with caption, column headers and row labels asserted."
CELL = re.compile(r"^(−?-?\d*\.\d+) \((\d*\.\d+)\)$")
for r in trs[2:]:
    model = txt(r[0])
    for j, (short, label, n, _) in enumerate(MZ_CELLS):
        printed = txt(r[1 + j])
        m = CELL.match(printed)
        assert m, printed
        val, se = m.group(1).replace("−", "-"), m.group(2)
        origin = "author_reported" if model == "TREDNet" else "independent_paper"
        ev = evaluation(f"manzo2025-{short.lower()}-{slug(model)}", f"{model} on {short} reporter variant effects", C[f"manzo2025-{slug(model)}"], PR[f"mz_{short}"],
                        D[f"mz_{short}"], [S_MZ], origin,
                        {"dataset_version": "As published", "split": "Per cell line", "population": f"{n} SNPs", "inputs": "1 kb reference and alternative sequences centred on the SNP",
                         "adaptation": mz_family(model)[2], "metric_implementation": "Pearson correlation of predicted and measured log2 fold-change", "aggregation": "As printed per cell line", "budget": None},
                        f"Table 1 row '{model}', column '{label}'")
        result(f"manzo2025-{short.lower()}-{slug(model)}-pearson", ev, [S_MZ], S_MZ, "pearson-correlation", printed.split(" (")[0], val,
               "predicted versus measured log2 fold-change of variant effect", f"Table 1 row '{model}', column '{label}'", HOW_T, "deterministic-table-parse", unit="unitless",
               uncertainty={"type": "standard_error", "value": se, "printed": f"({se})", "note": "Standard error as printed in brackets; its basis is not defined in the caption"})

# Tang Table 1
t = ET.parse(art["tk"]).getroot()
tw = [x for x in t.iter("table-wrap") if x.get("id") == "Tab1"][0]
assert txt(tw.find("caption")) == "Zero-shot variant effect generalization on CAGI5 dataset"
trs = list(tw.iter("tr"))
assert [txt(c) for c in trs[0]] == ["Training task", "Model", "HepG2", "K562"]
task, seen = None, []
for r in trs[1:]:
    cells = [txt(c) for c in r]
    if len(cells) == 4:
        task = cells[0]
        cells = cells[1:]
    assert len(cells) == 3
    model, hep, k5 = cells
    seen.append((task, model))
    key = TK_KEY[(task, model)]
    origin = "author_reported" if task.startswith("LentiMPRA") else "independent_paper"
    for cell, printed in (("HepG2", hep), ("K562", k5)):
        float(printed)
        ev = evaluation(f"tang2025-{cell.lower()}-{key.split('tang2025-')[1]}", f"{model} ({task}) on CAGI5 {cell}", C[key], PR[f"tk_{cell}"], D["tk"], [S_TK], origin,
                        {"dataset_version": "CAGI5 regulation challenge data", "split": "Zero-shot test", "population": "LDLR, SORT1, F9 (HepG2)" if cell == "HepG2" else "PKLR (K562)",
                         "inputs": "230 nt sequence centred on the CRE", "adaptation": TK_PARAMS[task], "metric_implementation": "Pearson correlation per experiment",
                         "aggregation": "Average over three CREs" if cell == "HepG2" else "Single CRE", "budget": None},
                        f"Table 1 row '{task}' / '{model}', column '{cell}'")
        result(f"tang2025-{cell.lower()}-{key.split('tang2025-')[1]}-pearson", ev, [S_TK], S_TK, "pearson-correlation", printed, printed,
               "predicted versus MPRA-measured saturation mutagenesis variant effect" + ("; mean over three CREs" if cell == "HepG2" else "; one CRE"),
               f"Table 1 row '{task}' / '{model}', column '{cell}'", HOW_T, "deterministic-table-parse", unit="unitless")
assert seen == TK_ROWS

# ---------------------------------------------------------------- descriptive claims
def claim(short, subject, field, value, srcs, src, locator):
    cid = f"{P}-claim-{short}"
    rec("claim", cid, f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.",
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
                    "date": DATE, "artifact_sha256": SHA[src], "retrieval_url": URL[src], "note": "Hand transcription from the article text. Pending independent review."}},
        srcs, links=[("subject", subject)])
    claims_rows.append([cid, src, locator, value, "claim"])


claim("gschwind2026-heldout-composition", D["gs_heldout"], "population_detail",
      "Held-out CRISPR data: 4,378 total E-G pairs and 190 (157.39 weighted) positives in K562, GM12878, HCT116, WTC11 and Jurkat cells, from eight CRISPR perturbation screens.",
      GSD, S_GS, "Figure 2 legend panel d; Methods 'Creating the combined held-out CRISPR dataset' paragraph 1")
claim("manzo2025-prose-averages", PR["mz_K562"], "reported_summary",
      "Results 2.1 reports averages across nine dataset-level Pearson correlations: TREDNet 0.297, ChromBPNet 0.289, SEI 0.276; Nucleotide Transformer v2 0.105. These averages are not the per-cell-line values of Table 1.",
      [S_MZ], S_MZ, "Results 2.1 paragraph 2")
claim("tang2025-finetuned-not-in-table", PR["tk_HepG2"], "scope_note",
      "gLMs fine-tuned on the lentiMPRA data also yielded improved performance (Additional file 1: Table S3); those values are not in Table 1.",
      [S_TK], S_TK, "Results 'Task 3: zero-shot variant effect prediction with MPRA data' paragraph 2")

# ---------------------------------------------------------------- judgements
CONSTR = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
          "Do not combine this mapping's evaluations with any other protocol's results, including the existing K562 CRISPRi and QTL mappings."]
J = []


def judgement(short, proto, endpoint, rationale, limitations, cites, group, title, headline, stratum=None, order=None):
    a = {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": "proxy", "endpoint": endpoint, "rationale": rationale, "constraints": CONSTR,
         "limitations": limitations, "citation_locators": [{"source_id": s, "locator": l} for s, l in cites],
         "source_locator": "; ".join(f"{s}: {l}" for s, l in cites), "revision": 1,
         "reason": "Recorded from the regulatory variant follow-up use-case pass 2026-10-09 (data/omics/use-case-coverage-regulatory-variant-20261009/).",
         "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        a["stratum_label"], a["stratum_order"] = stratum, order
    pname = next(r["name"] for r in records if r["id"] == proto)
    rec("claim", f"use-case-mapping-regulatory-variant-20261009-{short}", f'Relevance of {pname} to "{UC_NAME}"', rationale, a, sorted({s for s, _ in cites}), links=[("subject", UC)])
    J.append(proto)


E2G_RAT = ("Endogenous CRISPR perturbation of whole elements, scored against predictor links, informs which element-gene links to test for a locus. As with the existing K562 mapping, "
           "it does not cover allele editing or a causal disease role.")
judgement("gschwind2026-heldout", PR["gs_heldout"], "Weighted AUPRC, precision and recall at threshold, with 95% bootstrap intervals, for ENCODE-rE2G, ABC, EPIraction, EpiMap, distance to TSS and element-promoter correlation on held-out CRISPR pairs from five cell types",
          E2G_RAT + " The held-out pairs extend the evidence beyond the K562 training data.", GS_LIM,
          [(S_GS3, "Sheet 'Held-out benchmarks', Dataset 'Held-out'"), (S_GS, "Figure 2d legend; Methods 'Creating the combined held-out CRISPR dataset' and 'CRISPR benchmark'")],
          "gschwind2026-crispr", "CRISPR enhancer-gene benchmark, weighted metrics (Gschwind et al. 2026)", "auprc", "Held-out, five cell types", 1)
judgement("gschwind2026-k562-training", PR["gs_k562"], "The same weighted metrics on the combined K562 CRISPR pairs used to train ENCODE-rE2G",
          E2G_RAT + " Recorded beside the held-out stratum; ENCODE-rE2G values here are in-sample.",
          GS_LIM + ["In-sample for ENCODE-rE2G; same pairs as the existing K562 mapping, different weighting."],
          [(S_GS3, "Sheet 'Held-out benchmarks', Dataset 'Combined K562 (training)'")],
          "gschwind2026-crispr", "CRISPR enhancer-gene benchmark, weighted metrics (Gschwind et al. 2026)", "auprc", "Combined K562 training pairs", 2)
VAR_RAT = ("Agreement between predicted and measured allelic effects in reporter assays informs which variant-effect models to use when choosing alleles to edit. "
           "Reporter activity does not establish endogenous regulation or a disease role.")
for i, (short, label, n, desc) in enumerate(MZ_CELLS):
    judgement(f"manzo2025-{short.lower()}", PR[f"mz_{short}"], f"Pearson correlation (with standard error) between predicted and measured variant effects for 24 DNA language and sequence-to-function models on {n} {short} reporter-assay SNPs",
              VAR_RAT, MZ_LIM, [(S_MZ, f"Table 1 column '{label}'; Table 2; Table 4")], "manzo2025-reporter-variants",
              "Reporter-assay allelic effects across four cell lines (Manzo et al. 2025)", "pearson-correlation", short, i + 1)
for i, cell in enumerate(("HepG2", "K562")):
    judgement(f"tang2025-cagi5-{cell.lower()}", PR[f"tk_{cell}"], f"Pearson correlation between 14 zero-shot, embedding-probe and supervised models and CAGI5 saturation MPRA effects in {cell}",
              VAR_RAT, TK_LIM, [(S_TK, f"Table 1 column '{cell}'; Methods 'CAGI dataset'")], "tang2025-cagi5",
              "CAGI5 saturation mutagenesis MPRA (Tang et al. 2025)", "pearson-correlation", cell, i + 1)

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), [i for i, c in Counter(ids).items() if c > 1]
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
claims_rows.sort()
with open(os.path.join(OUT, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True))
print("judged protocols:", J)
