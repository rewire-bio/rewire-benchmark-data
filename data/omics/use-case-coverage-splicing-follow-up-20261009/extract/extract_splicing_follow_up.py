"""Deterministic extraction for the splicing follow-up use-case pass, 2026-10-09.

Usage: python3 -I extract_splicing_follow_up.py <download-dir> <batch-dir>

<download-dir> layout:
  PMC10734170/fulltext.xml, PMC10734170/supp.zip and PMC10734170/supp/13059_2023_3144_MOESM3_ESM.xlsx  (Smith and Kitzman 2023)
  PMC8360004/fulltext.xml                                                                             (Riepe et al. 2021)
  znabu2026/preprint.pdf                                                                              (Znabu et al. 2026 preprint)

Writes batch.jsonl and claims.csv to <batch-dir>. Extracts every cell of Smith and Kitzman
Additional file 3 (Table S2) sheet 'Sensitivity 10% SDV', Riepe et al. Tables 3-5, and the
Results table of Znabu et al. Row and column labels are asserted before values are read.
"""
import csv, hashlib, json, os, re, subprocess, sys, xml.etree.ElementTree as ET
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

DL, OUT = sys.argv[1], sys.argv[2]
P = "splicing-follow-up-20261009"
UC = "use-case-splicing-follow-up"
DATE = "2026-10-09"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
FAC = {"areas": ["dna-genomes"], "contexts": ["research"]}


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def txt(e):
    return " ".join("".join(e.itertext()).split())


def shortest(raw):
    s = repr(float(raw))
    return format(float(raw), "f") if ("e" in s or "E" in s) else s


records, claims_rows = [], []


def rec(kind, id_, name, description, attributes, source_ids, links=(), facets=None):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
         "facets": facets if facets is not None else {}, "source_ids": list(source_ids),
         "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attributes}
    records.append(r)
    return r["id"]


art = {"sk": os.path.join(DL, "PMC10734170", "fulltext.xml"),
       "sk_s2": os.path.join(DL, "PMC10734170", "supp", "13059_2023_3144_MOESM3_ESM.xlsx"),
       "sk_zip": os.path.join(DL, "PMC10734170", "supp.zip"),
       "riepe": os.path.join(DL, "PMC8360004", "fulltext.xml"),
       "znabu": os.path.join(DL, "znabu2026", "preprint.pdf")}
H = {k: sha(v) for k, v in art.items()}

S_SK, S_SK2 = f"{P}-source-smith2023", f"{P}-source-smith2023-table-s2"
S_RI, S_ZN = f"{P}-source-riepe2021", f"{P}-source-znabu2026"
ZN_PDF = "https://www.biorxiv.org/content/biorxiv/early/2026/07/26/2026.07.21.739871.full.pdf"
URL = {S_SK: EPMC + "PMC10734170/fullTextXML", S_SK2: EPMC + "PMC10734170/supplementaryFiles",
       S_RI: EPMC + "PMC8360004/fullTextXML", S_ZN: ZN_PDF}
SHA = {S_SK: H["sk"], S_SK2: H["sk_s2"], S_RI: H["riepe"], S_ZN: H["znabu"]}

rec("source", S_SK, "Benchmarking splice variant prediction algorithms using massively parallel splicing assays",
    "Primary source retrieved and hashed for the splicing follow-up use-case pass.",
    {"url": "https://doi.org/10.1186/s13059-023-03144-z", "artifact_url": URL[S_SK],
     "version": "Genome Biology 24:294, published 2023-12-21; PMC10734170 full-text XML", "retrieved_at": "2026-10-09T20:49:26Z",
     "artifact_sha256": H["sk"], "doi": "10.1186/s13059-023-03144-z", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/xml",
     "version_note": "The store already holds evidence-expansion-splice-evaluation-6960a140 for the same Europe PMC URL, retrieved 2026-09-17 with SHA-256 6960a140...; the bytes retrieved here differ, so a separate record pins them."},
    [], facets=FAC)
rec("source", S_SK2, "Smith and Kitzman 2023, Additional file 3 (Table S2)",
    "Workbook of transcriptome-normalised thresholds and sensitivities per tool and dataset.",
    {"url": "https://doi.org/10.1186/s13059-023-03144-z", "artifact_url": URL[S_SK2],
     "version": "13059_2023_3144_MOESM3_ESM.xlsx inside the Europe PMC supplementaryFiles zip for PMC10734170", "retrieved_at": "2026-10-09T20:49:34Z",
     "artifact_sha256": H["sk_s2"], "doi": "10.1186/s13059-023-03144-z", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
     "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
     "hash_scope": f"SHA-256 of the MOESM3 xlsx member (zip SHA-256 {H['sk_zip']}; Europe PMC assembles the zip per request)."},
    [], facets=FAC)
rec("source", S_RI, "Benchmarking deep learning splice prediction tools using functional splice assays",
    "Primary source retrieved and hashed for the splicing follow-up use-case pass.",
    {"url": "https://doi.org/10.1002/humu.24212", "artifact_url": URL[S_RI],
     "version": "Human Mutation 42(7):799, published online 2021-05-20; PMC8360004 full-text XML", "retrieved_at": "2026-10-09T20:52:02Z",
     "artifact_sha256": H["riepe"], "doi": "10.1002/humu.24212", "publication_status": "peer_reviewed", "licence": "CC-BY-NC-4.0",
     "media_type": "application/xml"}, [], facets=FAC)
rec("source", S_ZN, "A Reproducible MFASS Benchmark of Splice-Disruption Predictors Reveals a Shared Exon-Interior Blind Spot",
    "Preprint retrieved and hashed for the splicing follow-up use-case pass.",
    {"url": "https://doi.org/10.64898/2026.07.21.739871", "artifact_url": ZN_PDF,
     "version": "bioRxiv 2026.07.21.739871 v1, posted 2026-07-26; full-text PDF", "retrieved_at": "2026-10-09T20:52:21Z",
     "artifact_sha256": H["znabu"], "doi": "10.64898/2026.07.21.739871", "publication_status": "preprint", "licence": "CC-BY-4.0",
     "media_type": "application/pdf",
     "hash_scope": "SHA-256 of one retrieval. bioRxiv stamps the PDF ModDate at download (here 2026-10-09 21:52:24 BST), so a re-download gives different bytes; compare the text layer, not the file hash."},
    [], facets=FAC)

# ---------------------------------------------------------------- methods
M = {}


def method(short, name, desc, srcs, locator, mtype, access=None):
    a = {"reported_name": name, "entity_level": "method", "source_locator": locator,
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
    if access:
        a["access"] = access
    M[short] = rec("method", f"{P}-method-{short}", name, desc, a, srcs, facets=dict(FAC, method_types=[mtype]))


SL = "Smith and Kitzman Results 'Comparing bioinformatic predictions with MPSA measured effects' and Methods 'Scoring with eight splice effect predictors'"
RL = "Riepe et al. Table 1 and Methods 'In silico splice prediction tools'"
ZL = "Znabu et al. Section 3 'Predictors and scoring'"
SML = "supervised_machine_learning"
method("hal", "HAL", "Hexamer additive linear model of exon skipping; exonic variants only.", [S_SK], SL, SML,
       access="Web interface (http://splicing.cs.washington.edu/SE), per Smith and Kitzman Methods")
method("s-cap", "S-Cap", "Splicing clinically applicable pathogenicity classifier; precomputed scores.", [S_SK], SL, SML)
method("mmsplice", "MMSplice", "Modular deep model of exon, intron and splice-site effects on exon inclusion.", [S_SK, S_RI, S_ZN], "; ".join([SL, RL, ZL]), SML)
method("squirls", "SQUIRLS", "Random-forest splice-variant classifier using information-content and k-mer features.", [S_SK], SL, SML)
method("spanr", "SPANR (SPIDEX)", "Splicing-regulatory model of Xiong et al.; scores distributed as SPIDEX precomputed delta-PSI.", [S_SK, S_RI, S_ZN], "; ".join([SL, RL, ZL]), SML)
method("conspliceml", "ConSpliceML", "Splicing constraint and machine-learning meta-score; precomputed scores.", [S_SK], SL, SML)
method("splicetransformer", "SpliceTransformer", "Transformer predicting tissue-specific splicing.", [S_ZN], ZL, SML)
method("cadd", "CADD", "Combined annotation-dependent depletion score (SVM over more than 60 genomic features).", [S_RI], RL, SML)
method("dssp", "DSSP", "CNN with long short-term memory splice-site predictor (140 nt input).", [S_RI], RL, SML)
method("genesplicer", "GeneSplicer", "Decision tree and Markov model splice-site predictor.", [S_RI], RL, SML)
method("maxentscan", "MaxEntScan", "Maximum-entropy splice-site model.", [S_RI], RL, "conventional_pipeline")
method("nnsplice", "NNSPLICE", "Neural network splice-site predictor.", [S_RI], RL, SML)
method("splicerover", "SpliceRover", "CNN splice-site predictor.", [S_RI], RL, SML, access="Web site, per Riepe et al. Methods")
method("splicesitefinder-like", "SpliceSiteFinder-like", "Position weight matrix splice-site scorer.", [S_RI], RL, "conventional_pipeline")
method("alamut-consensus", "Alamut consensus 3/4", "Splice change called when 3 of 4 Alamut tools (GeneSplicer, MaxEntScan, NNSPLICE, SpliceSiteFinder-like) predict it.",
       [S_RI], "Riepe et al. Methods 'Classification metrics and receiver operator curve'", "conventional_pipeline")

# ---------------------------------------------------------------- configurations
C = {}


def config(key, short, name, of, srcs, mtype, version=None, version_note=None, params=None, locator=None, limitations=None):
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
    C[key] = rec("configuration", f"{P}-config-{short}", name, f"{name} as run in the cited comparison.", a, srcs,
                 links=[("configuration_of", of)], facets=dict(FAC, method_types=[mtype]))


# Smith and Kitzman thresholds (Table S2 sheet 'Thresholds', column 'Threshold for 10% SDV')
wb = rawxlsx.read(art["sk_s2"])
th = wb["Thresholds"]
assert [th.get(c) for c in ("B1", "C1", "D1")] == ["Threshold for 5% SDV", "Threshold for 10% SDV", "Threshold for 20% SDV"]
SK_TOOLS = ["HAL", "S-Cap", "MMSplice", "SQUIRLS", "SPANR", "SpliceAI", "Pangolin", "ConSpliceML"]
assert [th.get(f"A{i}") for i in range(2, 10)] == SK_TOOLS
TH10 = {t: shortest(th[f"C{i}"]) for i, t in zip(range(2, 10), SK_TOOLS)}
SKD = [S_SK, S_SK2]
MASK = "Masked or unmasked scores for Table S2 not stated (both were computed)."
SK_CFG = {
    "HAL": ("hal", M["hal"], None, "Version not printed; run through the web interface with wild-type PSI 90% (POU1F1), 50% (FAS), 60% (MST1R), 80% (BRCA1), 60% (WT1), 90% (MLH1)", None),
    "S-Cap": ("s-cap", M["s-cap"], None, "Precomputed 'sens' scores; version not printed", "Most severe of the dominant and recessive models at essential splice sites; transformed to 1 - score"),
    "MMSplice": ("mmsplice-2-2-0", M["mmsplice"], "2.2.0", None, "Default settings; delta logit PSI"),
    "SQUIRLS": ("squirls-1-0-0", M["squirls"], "1.0.0", None, "Default settings; default hg19 Ensembl annotation"),
    "SPANR": ("spanr-spidex", M["spanr"], None, "SPIDEX precomputed zdelta PSI scores; version not printed", None),
    "SpliceAI": ("spliceai-1-3-1", "catalog-model-spliceai", "1.3.1", None, "Distance set to exon length; MANE Select canonical annotation. " + MASK),
    "Pangolin": ("pangolin-1-0-2", "catalog-model-pangolin", "1.0.2", None, "Distance set to exon length; Pangolin_max score; MANE Select canonical annotation. " + MASK),
    "ConSpliceML": ("conspliceml", M["conspliceml"], None, "Precomputed scores matched by position and gene; version not printed", None),
}
for t, (short, of, ver, vnote, params) in SK_CFG.items():
    p = f"Transcriptome-normalised threshold calling 10% of 500,000 background SNVs: {TH10[t]} (Table S2 'Thresholds' column C)"
    if params:
        p = params + ". " + p
    lim = (["Benchmark variants scored with SpliceAI 1.3.1, but the background set used for the threshold came from SpliceAI 1.3 precomputed scores."] if t == "SpliceAI" else None)
    config(f"sk_{t}", f"smith2023-{short}", f"{t} (Smith and Kitzman 2023)", of, SKD,
           "conventional_pipeline" if t in () else SML, version=ver, version_note=vnote, params=p,
           locator="Methods 'Scoring with eight splice effect predictors'; Additional file 3 'Thresholds'", limitations=lim)

ALAMUT = "Alamut Visual 2.13"
RI_CFG = {
    "Alamut Consensus 3/4": ("alamut-consensus", M["alamut-consensus"], f"3 of 4 tools in {ALAMUT}", None, "conventional_pipeline"),
    "CADD": ("cadd-1-6", M["cadd"], "v1.6", None, SML),
    "DSSP": ("dssp", M["dssp"], None, "DSSP scripts from the DSSP GitHub; version not printed", SML),
    "GeneSplicer": ("genesplicer", M["genesplicer"], ALAMUT, None, SML),
    "MaxEntScan": ("maxentscan", M["maxentscan"], ALAMUT, None, "conventional_pipeline"),
    "MMSplice": ("mmsplice-2-0-0", M["mmsplice"], "v2.0.0", None, SML),
    "NNSPLICE": ("nnsplice", M["nnsplice"], ALAMUT, None, SML),
    "Spidex": ("spidex-1-0", M["spanr"], "SPIDEX v1.0", None, SML),
    "SpliceAI": ("spliceai-1-3-1", "catalog-model-spliceai", "v1.3.1", None, SML),
    "SpliceRover": ("splicerover", M["splicerover"], None, "Web site; version not printed", SML),
    "SpliceSiteFinder‐like": ("splicesitefinder-like", M["splicesitefinder-like"], ALAMUT, None, "conventional_pipeline"),
}
for t, (short, of, ver, vnote, mt) in RI_CFG.items():
    config(f"ri_{t}", f"riepe2021-{short}", f"{t.replace(chr(0x2010), '-')} (Riepe et al. 2021)", of, [S_RI], mt, version=ver, version_note=vnote,
           params="Classification cutoff per data set; Table 2 prints the ROC-optimal thresholds, and Tables 3-5 do not restate which cutoff was applied",
           locator="Methods 'In silico splice prediction tools'; Table 2")

ZN_CFG = {"Pangolin": ("pangolin", "catalog-model-pangolin", "Larger of maximum splice gain and maximum splice loss magnitude"),
          "SpliceAI": ("spliceai", "catalog-model-spliceai", "Maximum of the four delta scores"),
          "SpliceTransformer": ("splicetransformer", M["splicetransformer"], "Maximum change in acceptor or donor probability; tissue-agnostic channels"),
          "MMSplice": ("mmsplice", M["mmsplice"], "Magnitude of delta logit PSI; each MFASS exon reconstructed as an internal cassette exon"),
          "SPANR (legacy)": ("spanr", M["spanr"], "Magnitude of maximum-tissue delta index from the precomputed scores shipped with MFASS")}
for t, (short, of, params) in ZN_CFG.items():
    config(f"zn_{t}", f"znabu2026-{short}", f"{t} (Znabu et al. 2026)", of, [S_ZN], SML,
           version_note="Released weights used; software version not printed", params=params + "; hg38 genomic context", locator="Section 3 'Predictors and scoring'")

# ---------------------------------------------------------------- datasets and protocols
D, PR = {}, {}
SK_DATA = {
    "BRCA1": ("brca1-sge", "BRCA1 saturation genome editing, synonymous and intronic SNVs", "Saturation genome editing of 11 BRCA1 exons at the endogenous locus with RNA-seq splicing readout (Findlay et al.); synonymous and intronic variants only.", "proxy"),
    "FAS": ("fas-exon6-mpsa", "FAS exon 6 saturation MPSA", "Saturation minigene MPSA of FAS exon 6; SDV when category is skipping or inclusion.", "proxy"),
    "MLH1": ("mlh1-curated", "MLH1 curated clinical splicing variants", "296 MLH1 single-base substitutions curated from 77 publications, with splicing supported by patient blood RNA RT-PCR or minigene analysis; essential splice-site variants from Lynch syndrome patients included without molecular evidence; 160 splice-disruptive.", "outside_scope"),
    "POU1F1": ("pou1f1-exon2-mpsa", "POU1F1 exon 2 saturation MPSA", "Saturation minigene MPSA of POU1F1 exon 2 (alpha and beta acceptors).", "proxy"),
    "RON": ("mst1r-exon11-mpsa", "MST1R (RON) exon 11 saturation MPSA", "Saturation minigene MPSA of MST1R exon 11.", "proxy"),
    "WT1": ("wt1-exon9-mpsa", "WT1 exon 9 saturation MPSA", "Saturation minigene MPSA of WT1 exon 9 (KTS+ and KTS- donors).", "proxy"),
}
SK_PROTO = ("Label each benchmark variant splice-disruptive (SDV) or neutral as defined by its source study (intermediate variants removed). For each tool, take the score threshold at which "
            "it calls 10% of 500,000 random exonic and near-exonic background SNVs (MANE Select, internal coding exons +/- 100 bp) disruptive, and report sensitivity for benchmark SDVs at that threshold, "
            "overall and within exonic, intronic, and intronic-without-essential-splice-site variants.")
SK_LIM = ["Sensitivity only: the threshold fixes a genome-wide call rate, not specificity on the benchmark, so precision is not measured.",
          "Per-dataset SDV and neutral counts are not printed in Table S2.",
          "Blank cells (HAL intronic rows, FAS intronic columns) are not results and are not stored.",
          "Masking setting for SpliceAI and Pangolin in Table S2 is not stated."]
for col, (short, name, desc, rel) in SK_DATA.items():
    D[col] = rec("dataset", f"{P}-data-smith2023-{short}", f"{name} (Smith and Kitzman benchmark set)", desc,
                 {"version": "Additional file 2 Table S1 (as published)", "split": "No split; whole set is the benchmark",
                  "population": desc, "source_locator": "Results 'A validation set of variants and splice effects'; Methods 'Saturation mutagenesis datasets' and 'Manual curation of clinical MLH1 variants'",
                  "missing_metadata": {"variants": {"reason": "unextracted", "note": "Per-dataset counts are in Additional file 2 and Figure 1, not read"}}},
                 SKD, facets=FAC)
    lim = SK_LIM + (["Labels partly come from patient blood RNA and from pathogenicity rules (essential splice-site variants counted without molecular evidence); the use case excludes patient-RNA effects and pathogenicity."] if col == "MLH1" else [])
    PR[col] = rec("protocol", f"{P}-protocol-smith2023-{short}-tn10", f"{name}: transcriptome-normalised sensitivity at a 10% background call rate (Smith and Kitzman Table S2)",
                  "Sensitivity for experimentally labelled splice-disruptive SNVs at tool thresholds matched on genome-wide call rate.",
                  {"protocol": SK_PROTO, "version": "Additional file 3 (Table S2) sheet 'Sensitivity 10% SDV'",
                   "source_locator": f"Additional file 3 sheet 'Sensitivity 10% SDV', column '{col}'; Methods 'Statistical methods' and 'Random background variant set'",
                   "limitations": lim}, SKD, links=[("uses_data", D[col])], facets=FAC)

RI_DATA = {
    "t3": ("abca4-ncss", "ABCA4 noncanonical splice-site variants", 71, "71 ABCA4 variants near noncanonical splice sites from LOVD, ClinVar and ExAC, tested in midigenes in HEK293T (RT-PCR; more than 20% mutant RNA called splice-altering); 64 altered splicing. Selected for testing when at least two Alamut programs predicted a change.", "Table 3 | Confusion matrix and statistical measures of the ABCA4 NCSS variants"),
    "t4": ("abca4-di", "ABCA4 deep-intronic variants", 81, "81 ABCA4 deep-intronic variants tested in midigenes in HEK293T; 21 altered splicing. Selected when at least two Alamut programs predicted a change or a novel site of at least 75% relative strength.", "Table 4 | Confusion matrix and statistical measures of the ABCA4 DI variants"),
    "t5": ("mybpc3-ncss", "MYBPC3 noncanonical splice-site variants", 61, "61 MYBPC3 noncanonical splice-site variants tested in 500 bp minigenes (CMV promoter); splice-altering when RT-PCR transcripts differ from wild type (Fisher's exact p < .001); 34 altered splicing. Selected when MaxEntScan scored the variant below the reference.", "Table 5 | Confusion matrix and statistical measures of the MYBPC3 NCSS variants"),
}
RI_LIM = ["Variants were selected for testing with Alamut tools (ABCA4) or MaxEntScan (MYBPC3), which can favour those tools and their relatives.",
          "Cutoffs appear to be tuned on the same data set (Table 2 ROC-optimal thresholds); Tables 3-5 do not state the cutoff, so values may be optimistic.",
          "Small single-gene sets with strong class imbalance (ABCA4 NCSS 90% positive, ABCA4 DI 26% positive).",
          "Variants are from patients but splicing was measured in mini- or midigene assays in HEK293T, not in patient tissue."]
for k, (short, name, n, desc, cap) in RI_DATA.items():
    D[k] = rec("dataset", f"{P}-data-riepe2021-{short}", f"{name} (Riepe et al. benchmark set)", desc,
               {"version": "Riepe et al. Table S1 (as published)", "variants": n, "split": "No split; whole set is the benchmark", "population": desc,
                "source_locator": "Methods 'Datasets'; Results 'Variants'"}, [S_RI], facets=FAC)
    PR[k] = rec("protocol", f"{P}-protocol-riepe2021-{short}", f"{name}: classification against mini- or midigene splicing results (Riepe et al. {cap.split(' |')[0]})",
                "Binary classification of assay-measured splice alteration by splice prediction tools.",
                {"protocol": "Score each variant with each tool (missing Alamut scores set to zero); classify at a per-data-set cutoff and report the confusion matrix, accuracy, PPV, sensitivity, specificity, NPV and MCC (formulas in Table S2 of the article).",
                 "version": cap.split(" |")[0], "source_locator": f"{cap.split(' |')[0]}; Methods 'Classification metrics and receiver operator curve'", "limitations": RI_LIM,
                 "missing_metadata": {"metric_implementation": {"reason": "unreported", "note": "Cutoff applied in Tables 3-5 is not stated; analysis scripts are at github.com/cmbi/Benchmarking_splice_prediction_tools (not read)"}}},
                [S_RI], links=[("uses_data", D[k])], facets=FAC)

MFASS_DATA = "rewire-mfass-v2-dataset"
PR["zn"] = rec("protocol", f"{P}-protocol-znabu2026-mfass-full-cohort", "MFASS splice-disrupting variant detection, all 27,733 labelled SNVs (Znabu et al. 2026)",
               "Detection of MFASS splice-disrupting variants (exon inclusion reduced by at least 0.50) by sequence-based predictors scored in hg38 genomic context.",
               {"protocol": "Score all 28,972 mutant MFASS SNVs; drop variants without a v2 inclusion-change measurement, leaving 27,733 (1,050 SDVs, 3.79%). Report AUROC and average precision per tool, with 1,000-sample bootstrap 95% intervals for average precision.",
                "version": "bioRxiv v1, Section 4 Results table", "source_locator": "Section 2 'Data and ground truth'; Section 4 Results table",
                "limitations": ["Whole labelled MFASS cohort with no held-out split for the single-tool scores; not the rewire matched or v2 held-out populations, so do not pool with those protocols.",
                                "Preprint, not peer reviewed.", "Tissue-aware tools used tissue-agnostically; genomic context, not the minigene fragment, was scored.",
                                "SPANR scores cover 27,663 variants."]},
               [S_ZN], links=[("uses_data", MFASS_DATA)], facets=FAC)

# ---------------------------------------------------------------- evaluations and results
def evaluation(short, name, cfg, proto, data, srcs, comparison, locator, limitations=None, missing=None):
    a = {"origin": "independent_paper", "protocol": proto, "version": "Primary source as retrieved 2026-10-09",
         "comparison": dict(comparison, protocol_id=proto), "source_locator": locator}
    if limitations:
        a["limitations"] = limitations
    if missing:
        a["missing_metadata"] = missing
    return rec("evaluation", f"{P}-eval-{short}", name, "Published comparison; transcribed, not reproduced.", a, srcs,
               links=[("system", cfg), ("assessment", proto), ("data", data)], facets=FAC)


def result(short, ev, srcs, src, metric, direction, unit, printed, numeric, qualifier, locator, how, method,
           raw=None, uncertainty=None, unit_detail=None):
    a = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed, "numeric_value": numeric,
         "source_locator": locator,
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
    if unit_detail:
        a["unit_detail"] = unit_detail
    rid = f"{P}-result-{short}"
    rec("result", rid, f"{short} {metric}", "Reported measurement transcribed from the pinned source. Not independently reproduced.", a, srcs,
        links=[("evaluation", ev)])
    claims_rows.append([rid, src, locator, printed, "result"])


# Smith and Kitzman sheet 'Sensitivity 10% SDV'
sh = wb["Sensitivity 10% SDV"]
COLS = dict(zip("BCDEFG", ["BRCA1", "FAS", "MLH1", "POU1F1", "RON", "WT1"]))
for c, v in COLS.items():
    assert sh.get(f"{c}1") == v
CLASSES = [("", "all variants", 2), ("Exon_", "exonic variants", 10), ("Intron_", "intronic variants", 18), ("Intron_NonCanon_", "intronic variants excluding essential splice sites", 26)]
for prefix, _, start in CLASSES:
    for i, t in enumerate(SK_TOOLS):
        assert sh.get(f"A{start + i}") == prefix + t, (start + i, sh.get(f"A{start + i}"))
HOW_X = "Deterministic parse of the pinned XLSX cell XML (extract/extract_splicing_follow_up.py) with sheet name, dataset headers and row labels asserted; printed_value is the shortest round-trip decimal of the stored double, raw_xml_value keeps the stored text."
SK_EV = {}
for c, col in COLS.items():
    for t in SK_TOOLS:
        SK_EV[(col, t)] = evaluation(f"smith2023-{SK_DATA[col][0]}-{SK_CFG[t][0]}", f"{t} on {SK_DATA[col][1]}", C[f"sk_{t}"], PR[col], D[col], SKD,
                                     {"dataset_version": "Smith and Kitzman benchmark set (Additional file 2)", "split": "No split", "population": SK_DATA[col][2],
                                      "inputs": "SNV in genomic context with one MANE Select canonical transcript (SQUIRLS: default hg19 Ensembl)", "adaptation": "None; published models or precomputed scores",
                                      "metric_implementation": "Sensitivity at the tool threshold calling 10% of the 500,000-SNV background set", "aggregation": "Pooled over the dataset's variants, by variant class", "budget": None},
                                     f"Additional file 3 sheet 'Sensitivity 10% SDV', column {c} ('{col}'), rows for {t}")
        for prefix, label, start in CLASSES:
            row = start + SK_TOOLS.index(t)
            raw = sh.get(f"{c}{row}")
            if raw is None:
                continue
            v = shortest(raw)
            cls = (prefix.rstrip("_").lower().replace("_noncanon", "-noncanon") or "all")
            result(f"smith2023-{SK_DATA[col][0]}-{SK_CFG[t][0]}-{cls}", SK_EV[(col, t)], SKD, S_SK2, "recall", "higher", "fraction", v, v,
                   f"transcriptome-normalised threshold calling 10% of background SNVs; {label}",
                   f"Additional file 3 sheet 'Sensitivity 10% SDV', cell {c}{row}; row {prefix + t}, column {col}", HOW_X, "deterministic-table-parse", raw=raw)

# Riepe Tables 3-5
t = ET.parse(art["riepe"]).getroot()
HEAD = ["Tool", "Missing values", "TP", "FP", "TN", "FN", "Accuracy (%)", "PPV (%)", "Sensitivity (%)", "Specificity (%)", "NPV (%)", "MCC"]
RM = [("count", "lower", "count", "variants without a score"), ("true-positive-count", "higher", "count", None), ("false-positive-count", "lower", "count", None),
      ("true-negative-count", "higher", "count", None), ("false-negative-count", "lower", "count", None), ("accuracy", "higher", "percent", None),
      ("precision", "higher", "percent", None), ("recall", "higher", "percent", None), ("specificity", "higher", "percent", None),
      ("negative-predictive-value", "higher", "percent", None), ("matthews-correlation-coefficient", "higher", "unitless", None)]
RSHORT = ["missing", "tp", "fp", "tn", "fn", "accuracy", "ppv", "sensitivity", "specificity", "npv", "mcc"]
EXPECT = {"t3": list(RI_CFG), "t4": [k for k in RI_CFG if k not in ("MMSplice", "Spidex")], "t5": list(RI_CFG)}
HOW_T = "Deterministic parse of the pinned article XML table (extract/extract_splicing_follow_up.py) with caption, column headers and tool labels asserted."
for k, tid in (("t3", "humu24212-tbl-0003"), ("t4", "humu24212-tbl-0004"), ("t5", "humu24212-tbl-0005")):
    tw = [x for x in t.iter("table-wrap") if x.get("id") == tid][0]
    cap = txt(tw.find("caption"))
    assert cap == RI_DATA[k][4].split(" | ")[1], cap
    trs = list(tw.iter("tr"))
    assert [txt(c) for c in trs[0]] == HEAD
    assert [txt(r[0]) for r in trs[1:]] == EXPECT[k]
    tab = RI_DATA[k][4].split(" |")[0]
    for r in trs[1:]:
        tool = txt(r[0])
        ev = evaluation(f"riepe2021-{RI_DATA[k][0]}-{RI_CFG[tool][0]}", f"{tool.replace(chr(0x2010), '-')} on {RI_DATA[k][1]}", C[f"ri_{tool}"], PR[k], D[k], [S_RI],
                        {"dataset_version": "Riepe et al. Table S1 (as published)", "split": "No split", "population": f"{RI_DATA[k][2]} variants",
                         "inputs": "Variant (GRCh37) as VCF, FASTA window or Alamut session, per tool", "adaptation": "Per-data-set cutoff",
                         "metric_implementation": None, "aggregation": "Pooled over the data set", "budget": None},
                        f"{tab} row '{tool}'", missing={"metric_implementation": {"reason": "unreported", "note": "Cutoff used in this table not stated"}})
        for j, (metric, d, unit, q) in enumerate(RM):
            printed = txt(r[1 + j])
            float(printed)
            result(f"riepe2021-{RI_DATA[k][0]}-{RI_CFG[tool][0]}-{RSHORT[j]}", ev, [S_RI], S_RI, metric, d, unit, printed, printed, q,
                   f"{tab} row '{tool}', column '{HEAD[1 + j]}'", HOW_T, "deterministic-table-parse",
                   unit_detail=("variants" if unit == "count" else None))

# Znabu Results table (PDF text layer)
text = subprocess.run(["pdftotext", "-layout", art["znabu"], "-"], capture_output=True, text=True, check=True).stdout
lines = text.splitlines()
hi = [i for i, l in enumerate(lines) if re.match(r"^\s*predictor\s+n\s+AUROC\s+AP\s+AP 95% CI\s*$", l)]
assert len(hi) == 1
ROW = re.compile(r"^\s*(Pangolin|SpliceAI|SpliceTransformer|MMSplice|SPANR \(legacy\))\s+([\d,]+)\s+([\d.]+)\s+([\d.]+)\s+\[([\d.]+), ([\d.]+)\]\s*$")
rows = [ROW.match(l) for l in lines[hi[0] + 1: hi[0] + 6]]
assert all(rows) and [m.group(1) for m in rows] == list(ZN_CFG)
assert "Confidence intervals are 1,000-sample bootstraps of the average precision." in text
HOW_P = "Deterministic parse of the pinned PDF text layer (pdftotext -layout) with the header line and five row labels asserted by regular expression."
LOC = "Section 4 'Results' table (page 3)"
for m in rows:
    tool, n, auroc, ap, lo, hi_ = m.groups()
    short = ZN_CFG[tool][0]
    ev = evaluation(f"znabu2026-{short}", f"{tool} on all labelled MFASS SNVs", C[f"zn_{tool}"], PR["zn"], MFASS_DATA, [S_ZN],
                    {"dataset_version": "MFASS public processed table (hg38), v2 inclusion labels", "split": "None (whole labelled cohort)",
                     "population": f"{n} scored of 27,733 labelled MFASS SNVs", "inputs": "hg38 genomic context, reference versus alternate",
                     "adaptation": "None; published weights", "metric_implementation": "AUROC and average precision", "aggregation": "Pooled over variants", "budget": None},
                    f"{LOC}, row '{tool}'")
    result(f"znabu2026-{short}-n", ev, [S_ZN], S_ZN, "count", "unknown", "count", n, n.replace(",", ""), "variants scored", f"{LOC}, row '{tool}', column 'n'",
           HOW_P, "pdf-text-parse", unit_detail="variants")
    result(f"znabu2026-{short}-auroc", ev, [S_ZN], S_ZN, "auroc", "higher", "fraction", auroc, auroc, None, f"{LOC}, row '{tool}', column 'AUROC'", HOW_P, "pdf-text-parse")
    result(f"znabu2026-{short}-ap", ev, [S_ZN], S_ZN, "average-precision", "higher", "fraction", ap, ap, None, f"{LOC}, row '{tool}', columns 'AP' and 'AP 95% CI'",
           HOW_P, "pdf-text-parse",
           uncertainty={"type": "confidence_interval", "printed": f"[{lo}, {hi_}]", "lower": lo, "upper": hi_, "level": 0.95, "method": "bootstrap", "resamples": 1000,
                        "source_column": "AP 95% CI"})

# ---------------------------------------------------------------- descriptive claims
def claim(short, subject, field, value, srcs, src, locator):
    cid = f"{P}-claim-{short}"
    rec("claim", cid, f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.",
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
                    "date": DATE, "artifact_sha256": SHA[src], "retrieval_url": URL[src], "note": "Hand transcription from the source text. Pending independent review."}},
        srcs, links=[("subject", subject)])
    claims_rows.append([cid, src, locator, value, "claim"])


claim("smith2023-median-tn-sensitivity", PR["BRCA1"], "reported_summary",
      "Transcriptome-normalised sensitivity varied widely between algorithms, but SpliceAI, ConSpliceML, and Pangolin emerged as consistent leaders (median across datasets of 87.3%, 85.8%, and 79.9%, respectively).",
      SKD, S_SK, "Results 'Benchmarking in the context of genome-wide prediction' paragraph 2")
claim("riepe2021-selection", PR["t3"], "selection_bias",
      "The selection criterion for functional validation of the ABCA4 variants was a 2% difference in splice score for at least two of the Alamut programs; for MYBPC3 variants, the selection criterion was a lower MaxEntScan score than the score of the reference nucleotide.",
      [S_RI], S_RI, "Methods 'Datasets' paragraph 2")
claim("riepe2021-mmsplice-spidex-di-excluded", PR["t4"], "allowed_information",
      "MMSplice and Spidex could not calculate a score for more than half of the ABCA4 DI variants and were excluded from the DI analysis.",
      [S_RI], S_RI, "Methods 'In silico splice prediction tools' paragraph 3")
claim("znabu2026-shared-misses", PR["zn"], "reported_finding",
      "200 of 1,050 disrupting variants (19%) are missed by all five tools at a common 10% false-positive operating point; 77% of these lie more than 10 bp from a splice site and 149 of 200 are exonic.",
      [S_ZN], S_ZN, "Section 5 'Where the tools fail' paragraph 3")

# ---------------------------------------------------------------- relevance judgements
CONSTR = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
          "Do not combine this mapping's evaluations with any other protocol's results, including the matched and historical MFASS protocols; populations, labels and thresholds differ."]
J = []


def judgement(short, proto, relevance, endpoint, rationale, limitations, cites, group, title, headline, stratum=None, order=None):
    a = {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": relevance, "endpoint": endpoint, "rationale": rationale,
         "constraints": CONSTR, "limitations": limitations, "citation_locators": [{"source_id": s, "locator": l} for s, l in cites],
         "source_locator": "; ".join(f"{s}: {l}" for s, l in cites), "revision": 1,
         "reason": "Recorded from the splicing follow-up use-case pass 2026-10-09 (data/omics/use-case-coverage-splicing-follow-up-20261009/).",
         "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        a["stratum_label"], a["stratum_order"] = stratum, order
    pname = next(r["name"] for r in records if r["id"] == proto)
    rec("claim", f"use-case-mapping-splicing-follow-up-20261009-{short}", f'Relevance of {pname} to "Prioritise variants for splicing experiments"',
        rationale, a, sorted({s for s, _ in cites}), links=[("subject", UC)])
    J.append(proto)


ASSAY_RAT = ("Experimentally measured splicing of human SNVs, with several predictors scored on the same variants, informs which configurations to use when choosing SNVs for a follow-up "
             "splicing experiment. As for the existing MFASS mappings, transfer to a different assay, exon or follow-up capacity is not established.")
for i, col in enumerate(["BRCA1", "FAS", "MLH1", "POU1F1", "RON", "WT1"]):
    short, name, desc, rel = SK_DATA[col]
    if rel == "outside_scope":
        rat = ("Labels mix patient blood RNA, minigene results and a pathogenicity rule for essential splice-site variants, which the use case excludes; recorded so the "
               "column is not mistaken for assay-only evidence.")
    else:
        rat = ASSAY_RAT
    judgement(f"smith2023-{short}", PR[col], rel,
              f"Sensitivity for {name} splice-disruptive SNVs at thresholds calling 10% of 500,000 background SNVs, for HAL, S-Cap, MMSplice, SQUIRLS, SPANR, SpliceAI, Pangolin and ConSpliceML, overall and by variant class",
              rat, SK_LIM + (["Labels include patient RNA and pathogenicity-based calls."] if rel == "outside_scope" else []),
              [(S_SK2, f"Sheet 'Sensitivity 10% SDV', column '{col}'; sheet 'Thresholds' column C"), (S_SK, "Results 'Benchmarking in the context of genome-wide prediction'; Methods")],
              "smith2023-mpsa-tn10", "Saturation splicing assays, sensitivity at a 10% genome-wide call rate (Smith and Kitzman 2023)", "recall", name, i + 1)
for i, k in enumerate(["t3", "t4", "t5"]):
    short, name, n, desc, cap = RI_DATA[k]
    judgement(f"riepe2021-{short}", PR[k], "proxy",
              f"Confusion matrix, accuracy, PPV, sensitivity, specificity, NPV and MCC for up to 11 splice predictors on {n} {name} tested in mini- or midigene assays",
              ASSAY_RAT, RI_LIM, [(S_RI, f"{cap.split(' |')[0]}; Methods 'Datasets' and 'In silico splice prediction tools'")],
              "riepe2021-minigene", "ABCA4 and MYBPC3 mini- and midigene variant sets (Riepe et al. 2021)", "matthews-correlation-coefficient", name, i + 1)
judgement("znabu2026-mfass", PR["zn"], "proxy",
          "AUROC and average precision (with bootstrap 95% intervals) for Pangolin, SpliceAI, SpliceTransformer, MMSplice and SPANR on all 27,733 labelled MFASS SNVs",
          ASSAY_RAT + " This is a separate MFASS population from the matched-annotation and v2 held-out protocols and must not be pooled with them.",
          ["Preprint, not peer reviewed; independent authors.", "Whole labelled cohort, not a held-out split; SPANR scored 27,663 variants.",
           "The 27,733 count matches rewire-mfass-v2-dataset; variant-level identity was not checked.", "Reporter exon inclusion, not patient RNA or pathogenicity."],
          [(S_ZN, "Section 4 Results table; Sections 2 and 3")], "znabu2026-mfass", "MFASS full labelled cohort (Znabu et al. 2026 preprint)", "average-precision")

# ---------------------------------------------------------------- write
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
