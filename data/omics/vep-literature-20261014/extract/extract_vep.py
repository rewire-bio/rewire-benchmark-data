"""Build the vep-literature-20261014 batch from pinned source bytes.

Usage:
  python3 -I extract/extract_vep.py <download-dir> <batch-dir>

<download-dir> holds the retrieved artifacts:
  PMC12016141.xml                       Europe PMC full text of Livesey and Marsh 2025 (Genome Biol 26:104)
  gb2025/MOESM2_ESM.xlsx                its Supplementary Material 2 (Tables S1-S8)
  pg/<path with / replaced by _>.csv    four ProteinGym summary CSVs at commit 144fe22

Every artifact hash, sheet header, row label set and row count is asserted before anything is
written. Values are transcribed from the workbook cells and CSV text; nothing is computed except
the shortest round-trip decimal of each stored workbook number (the cells use the General format).
Writes batch.jsonl and claims.csv. All records are status needs_review: this is an extraction,
not a review.
"""
import csv
import hashlib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ooxml import read_sheets  # noqa: E402

P = "vep-lit-20261014"
DATE = "2026-10-14"
PG_COMMIT = "144fe22b07dfaeec2b366f2346203a9838a55b4c"
PG_RAW = f"https://raw.githubusercontent.com/OATML-Markslab/ProteinGym/{PG_COMMIT}/"
PG_BLOB = f"https://github.com/OATML-Markslab/ProteinGym/blob/{PG_COMMIT}/"

ART = {
    "xml": ("PMC12016141.xml", "1735ee461ef192d9de67c914e9ad73d72d8aa255ea0e3479eb68cd8631d99fa2",
            "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12016141/fullTextXML", "2026-10-14T13:36:01Z"),
    "supp": ("gb2025/MOESM2_ESM.xlsx", "1b0d792d1a5d3daa95545a7973cabb131c45e42c952e7e5a447a72deef1d1e70",
             "https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-025-03575-w/MediaObjects/13059_2025_3575_MOESM2_ESM.xlsx",
             "2026-10-14T13:36:25Z"),
    "pg_dms": ("pg/benchmarks_DMS_zero_shot_substitutions_Spearman_Summary_performance_DMS_substitutions_Spearman.csv",
               "ee61a7c09efbfbd8d9a6c9355092c798032a578fa58c6f6256b5da8778555fd4",
               PG_RAW + "benchmarks/DMS_zero_shot/substitutions/Spearman/Summary_performance_DMS_substitutions_Spearman.csv",
               "2026-10-14T13:39:32Z"),
    "pg_czs": ("pg/benchmarks_clinical_zero_shot_substitutions_AUC_Summary_performance_clinical_substitutions_AUC.csv",
               "fbe453d1aaa6c30a1d0adf610f7fc23c36044a8e2548b178d316777383f8fe93",
               PG_RAW + "benchmarks/clinical_zero_shot/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv",
               "2026-10-14T13:39:33Z"),
    "pg_css": ("pg/benchmarks_clinical_supervised_substitutions_AUC_Summary_performance_clinical_substitutions_AUC.csv",
               "f2e38aeac2624d87e7a35a5b16bd580de62c24db36973848e1d94ac3ce510359",
               PG_RAW + "benchmarks/clinical_supervised/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv",
               "2026-10-14T13:39:33Z"),
    "pg_czi": ("pg/benchmarks_clinical_zero_shot_indels_AUC_Summary_performance_clinical_indels_AUC.csv",
               "98a532c0e2c3d4720b73b7c05cf0dcf0419438c326761aaae3b788799f5aa836",
               PG_RAW + "benchmarks/clinical_zero_shot/indels/AUC/Summary_performance_clinical_indels_AUC.csv",
               "2026-10-14T13:39:33Z"),
}

# Existing store records reused unchanged.
PG_SCRIPT_SOURCE = "profile-protocol-proteingym-proteingym-performance-dms-benchmarks-py-0002bc1b"
PG_README_SOURCE = "run-doc-proteingym-readme-md-144fe22b"
PG_REFERENCE_SOURCE = "profile-protocol-proteingym-reference-files-dms-substitutions-csv-a8f49801"
PG_BENCHMARK = "discovery-benchmark-proteingym"
PG_DMS_PROTOCOL = "rewire-proteingym-v1-3-dms-substitutions"

S_ART = f"{P}-source-livesey2025-article"
S_SUPP = f"{P}-source-livesey2025-supplementary-2"
S_PG = {
    "pg_dms": f"{P}-source-proteingym-dms-substitutions-spearman-summary-144fe22",
    "pg_czs": f"{P}-source-proteingym-clinical-zero-shot-substitutions-auc-summary-144fe22",
    "pg_css": f"{P}-source-proteingym-clinical-supervised-substitutions-auc-summary-144fe22",
    "pg_czi": f"{P}-source-proteingym-clinical-zero-shot-indels-auc-summary-144fe22",
}

COLLECTOR_NOTE = ("Collector agent for the 2026-10-14 VEP literature pass (Claude Opus 5.5); extraction only, "
                  "not a review. Pending an independent review-evidence pass.")


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def slug(text):
    s = text.lower().replace("&", "and").replace("+", "plus")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def short_decimal(raw):
    """Shortest round-trip decimal of a stored workbook number, without exponent."""
    value = float(raw)
    text = repr(value)
    if "e" in text or "E" in text:
        text = format(value, "f")
    if text.endswith(".0"):
        text = text[:-2]
    return text


def review(key, method_note, note):
    return {
        "method": ["deterministic-table-parse"],
        "method_note": method_note,
        "reviewer": ["claude"],
        "reviewer_note": COLLECTOR_NOTE,
        "date": DATE,
        "artifact_sha256": ART[key][1],
        "retrieval_url": ART[key][2],
        "note": note,
    }


def doc_review(key, note):
    return {
        "method": ["ai-assisted-source-review"],
        "method_note": "Read by the collector agent from the pinned artifact.",
        "reviewer": ["claude"],
        "reviewer_note": COLLECTOR_NOTE,
        "date": DATE,
        "artifact_sha256": ART[key][1],
        "retrieval_url": ART[key][2],
        "note": note,
    }


records = []
claims_rows = []


def add(record):
    records.append(record)
    return record["id"]


# ---------------------------------------------------------------------------------------------
# Load and check artifacts
# ---------------------------------------------------------------------------------------------
dl, out = sys.argv[1], sys.argv[2]
paths = {}
for key, (rel, digest, _url, _t) in ART.items():
    path = os.path.join(dl, rel)
    got = sha(path)
    assert got == digest, f"{key}: hash {got} != {digest}"
    paths[key] = path

xml_root = ET.parse(paths["xml"]).getroot()
title = "".join(xml_root.find(".//article-meta/title-group/article-title").itertext())
assert title == "Variant effect predictor correlation with functional assays is reflective of clinical classification performance", title
body_text = "".join(xml_root.find(".//body").itertext())
for phrase in ["assessing the performance of 97 VEPs", "819 proteins that had at least 10 (likely) pathogenic",
               "The full ranking of all available predictors is provided in Additional file 2: Table S8",
               "The final rank score was calculated by averaging the win rate of each VEP against all other VEPs"]:
    assert phrase in "".join(xml_root.itertext()), phrase

sheets = read_sheets(paths["supp"])
assert list(sheets) == ["Legends", "Table S1", "Table S2", "Table S3", "Table S4", "Table S5", "Table S6",
                        "Table S7", "Table S8", "References"], list(sheets)


def grid(name):
    rows = {}
    for ref, (value, formula, _style) in sheets[name].items():
        m = re.match(r"([A-Z]+)(\d+)$", ref)
        col = 0
        for ch in m.group(1):
            col = col * 26 + ord(ch) - 64
        rows.setdefault(int(m.group(2)), {})[col] = (ref, value, formula)
    return rows


def colname(n):
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


legends = {ref: v for ref, (v, _f, _s) in sheets["Legends"].items()}
assert legends["A6"] == "Table S3: Full matrix of pairwise win-rates from the DMS benchmark (data used for Figure 2)."
assert legends["A11"] == "Table S8: Full matrix of pairwise win-rates from the AUROC benchmark (data used for Figure 3)."
assert legends["A8"].startswith("Table S5: The DMS benchmark rank score when only direct DMS assays")
assert legends["A9"] == "Table S6: The DMS benchmark rank score when limited to only substitutions possible by single nucleotide variants."
assert legends["A10"].startswith("Table S7:\xa0The DMS benchmark rank score when limited to only substitutions possible by single nucleotide variants and prediction gaps are filled")

# Table S2: VEP types and prediction sources
s2 = grid("Table S2")
assert [s2[1][c][1] for c in range(1, 6)] == ["Predictor", "Type", "Source", "DMS sets used for training", "Reference"]
S2 = {}
for r in sorted(s2)[1:]:
    label = s2[r][1][1]
    S2[label] = {
        "row": r,
        "type": s2[r][2][1],
        "source": s2[r][3][1],
        "dms_training": s2[r].get(4, (None, None, None))[1],
        "reference": s2[r][5][1],
    }
assert len(S2) == 93, len(S2)


def summary_table(name, label_cols):
    g = grid(name)
    header = {c: v for c, (_ref, v, _f) in g[1].items()}
    cols = {v: c for c, v in header.items()}
    assert header[1] == "VEP"
    out_rows = []
    for r in sorted(g)[1:]:
        row = {"_row": r, "VEP": g[r][1][1]}
        for lab in label_cols:
            ref, value, formula = g[r][cols[lab]]
            assert formula is None, f"{name} {ref} has a formula"
            row[lab] = (ref, value)
        out_rows.append(row)
    return out_rows, header


S3_ROWS, s3_header = summary_table("Table S3", ["rank_score", "proteins", "top_5_winrate"])
S5_ROWS, s5_header = summary_table("Table S5", ["rank_score_indirect", "rank_score_direct"])
assert s5_header[4] == "absolute_difference"  # a formula column (difference of the two), not extracted
S6_ROWS, _ = summary_table("Table S6", ["rank_score", "proteins"])
S7_ROWS, _ = summary_table("Table S7", ["rank_score", "proteins"])
S8_ROWS, s8_header = summary_table("Table S8", ["rank_score", "proteins"])
assert len(S3_ROWS) == 97 and len(S5_ROWS) == 97 and len(S6_ROWS) == 97 and len(S7_ROWS) == 97, "row counts"
assert len(S8_ROWS) == 85, len(S8_ROWS)
assert len(s3_header) == 101 and s3_header[99] == "rank_score" and s3_header[100] == "proteins" and s3_header[101] == "top_5_winrate"
assert s8_header[87] == "rank_score" and s8_header[88] == "proteins" and len(s8_header) == 88
S3_NAMES = {row["VEP"] for row in S3_ROWS}
for rows in (S5_ROWS, S6_ROWS, S7_ROWS):
    assert {row["VEP"] for row in rows} == S3_NAMES
S8_NAMES = {row["VEP"] for row in S8_ROWS}
assert S8_NAMES - S3_NAMES == {"CADD", "COSMIS", "CPT", "fathmm-XF"}, S8_NAMES - S3_NAMES

# ---------------------------------------------------------------------------------------------
# VEP identities: printed label -> (configuration slug, Table S2 label, target record, method types)
# A target starting with "new:" is a method record created in this batch.
# ---------------------------------------------------------------------------------------------
SO = "somatic-oncogenicity-20261009-method-"
UC = "uc20260930-model-"
FM, SML, SP, CP = "foundation_model", "supervised_machine_learning", "specialist", "conventional_pipeline"
VEP = {
    "3Cnet": ("3cnet", "3Cnet", "new:3cnet", [SML]),
    "AlphScore": ("alphscore", "AlphScore", "new:alphscore", [SML]),
    "AlphaMissense": ("alphamissense", "AlphaMissense", SO + "alphamissense", [SML]),
    "BLOSUM62": ("blosum62", "BLOSUM62", "flip-method-blosum62", [CP]),
    "BayesDel": ("bayesdel", "BayesDel and BayesDel noAF", "uc-clinical-20260930-method-bayesdel", [SML]),
    "BayesDel_noAF": ("bayesdel-noaf", "BayesDel and BayesDel noAF", "uc-clinical-20260930-method-bayesdel", [SML]),
    "CADD_1.6": ("cadd-1-6", "CADD 1.6", SO + "cadd", [SML]),
    "CADD_1.7": ("cadd-1-7", "CADD 1.7", SO + "cadd", [SML]),
    "CADD": ("cadd-unversioned", None, SO + "cadd", [SML]),
    "CAPICE": ("capice", "CAPICE", "new:capice", [SML]),
    "CARP": ("carp", "CARP", UC + "carp", [FM]),
    "CONDEL": ("condel", "CONDEL", "brca-20261009-method-condel", [SP]),
    "COSMIS": ("cosmis", None, "new:cosmis", [SP]),
    "CPT-1": ("cpt-1", "CPT-1", "new:cpt", [SML]),
    "ClinPred": ("clinpred", "ClinPred", SO + "clinpred", [SML]),
    "DANN": ("dann", "DANN", SO + "dann", [SML]),
    "DEOGEN2": ("deogen2", "DEOGEN2", SO + "deogen2", [SML]),
    "DeMaSk": ("demask", "DeMaSk", "new:demask", [SML]),
    "DeepSAV": ("deepsav", "DeepSAV", "new:deepsav", [SML]),
    "DeepSequence": ("deepsequence", "DeepSequence", UC + "deepsequence", [SP]),
    "ESCOTT": ("escott", "ESCOTT", UC + "escott", [SP]),
    "ESM-1b": ("esm-1b", "ESM-1b", UC + "esm-1b", [FM]),
    "ESM-1v": ("esm-1v", "ESM-1v", "discovery-model-esm-1v", [FM]),
    "ESM2": ("esm2", "ESM2", "discovery-model-esm-2", [FM]),
    "EVE": ("eve", "EVE", UC + "eve", [SP]),
    "EVmutation_epistatic": ("evmutation-epistatic", "Evmutation (independent and epsitatic models", "uc20260930-method-evmutation", [SP]),
    "EVmutation_independent": ("evmutation-independent", "Evmutation (independent and epsitatic models", "uc20260930-method-evmutation", [SP]),
    "Eigen": ("eigen", "Eigen", SO + "eigen", [SP]),
    "Envision": ("envision", "Envision", "new:envision", [SML]),
    "FATHMM": ("fathmm", "Fathmm", SO + "fathmm", [SP]),
    "FathmmXF": ("fathmm-xf", "Fathmm-XF", SO + "fathmm-xf", [SML]),
    "GEMME": ("gemme", "GEMME", "uc20260930-method-gemme", [SP]),
    "GERP++": ("gerp-plus-plus", "GERP++", SO + "gerp", [SP]),
    "GenoCanyon": ("genocanyon", "GenoCanyon", SO + "genocanyon", [SP]),
    "Grantham": ("grantham", "Grantham", "brca-20261009-method-grantham", [SP]),
    "InMeRF": ("inmerf", "InMeRF", "new:inmerf", [SML]),
    "LASSIE": ("lassie", "LASSIE", "new:lassie", [SP]),
    "LIST-S2": ("list-s2", "LIST-S2", SO + "list-s2", [SP]),
    "LRT": ("lrt", "LRT", SO + "lrt", [SP]),
    "M-CAP": ("m-cap", "M-CAP", SO + "m-cap", [SML]),
    "MISTIC": ("mistic", "MISTIC", "new:mistic", [SML]),
    "MOIpred_benign": ("moipred-benign", "MOIpred", "new:moi-pred", [SML]),
    "MPC": ("mpc", "MPC", SO + "mpc", [SML]),
    "MSA_Transformer": ("msa-transformer", "MSA Transformer", UC + "msa-transformer", [FM]),
    "MVP": ("mvp", "MVP", SO + "mvp", [SML]),
    "Maverick_benign": ("maverick-benign", "Maverick", "new:maverick", [SML]),
    "MetaLR": ("metalr", "MetaLR", SO + "metalr", [SML]),
    "MetaRNN": ("metarnn", "MetaRNN", SO + "metarnn", [SML]),
    "MetaSVM": ("metasvm", "MetaSVM", SO + "metasvm", [SML]),
    "MutFormer": ("mutformer", "Mutformer", SO + "mutformer", [SML]),
    "MutPred": ("mutpred", "MutPred", SO + "mutpred", [SML]),
    "MutScore": ("mutscore", "MutScore", SO + "mutscore", [SML]),
    "MutationAssessor": ("mutationassessor", "MutationAssessor", SO + "mutationassessor", [SP]),
    "PANTHER": ("panther", "PANTHER", "brca-20261009-method-panther-psep", [SP]),
    "PHACT": ("phact", "PHACT", "new:phact", [SP]),
    "PHACTboost": ("phactboost", "PHACTboost", SO + "phactboost", [SML]),
    "PROVEAN": ("provean", "PROVEAN", SO + "provean", [CP]),
    "PhD-SNPg": ("phd-snpg", "PhD_SNPg", "brca-20261009-method-phd-snpg", [SML]),
    "PhD_SNP": ("phd-snp", "PhD_SNP", "new:phd-snp", [SML]),
    "PolyPhen2_HumDiv": ("polyphen2-humdiv", "PolyPhen2 HumVar and HumDiv models", SO + "polyphen2", [SML]),
    "PolyPhen2_HumVar": ("polyphen2-humvar", "PolyPhen2 HumVar and HumDiv models", SO + "polyphen2", [SML]),
    "PonP2": ("ponp2", "PonP2", "brca-20261009-method-pon-p2", [SML]),
    "PrimateAI": ("primateai", "PrimateAI", SO + "primateai", [SML]),
    "ProGen2": ("progen2", "ProGen2", UC + "progen2", [FM]),
    "ProtGPT2": ("protgpt2", "ProtGPT2", UC + "protgpt2", [FM]),
    "REVEL": ("revel", "REVEL", SO + "revel", [SML]),
    "RITA": ("rita", "RITA", UC + "rita", [FM]),
    "Rhapsody": ("rhapsody", "Rhapsody", "new:rhapsody", [SML]),
    "SIFT": ("sift", "SIFT", SO + "sift", [CP]),
    "SIFT4G": ("sift4g", "SIFT4G", SO + "sift", [CP]),
    "SIGMA": ("sigma", "SIGMA", "new:sigma", [SML]),
    "SNAP2": ("snap2", "SNAP2", "brca-20261009-method-snap2", [SML]),
    "SNPred": ("snpred", "SNPred", "new:snpred", [SML]),
    "SNPs&GO": ("snps-and-go", "SNPs&GO", "new:snps-and-go", [SML]),
    "SNPs&GO3D": ("snps-and-go3d", "SNPs&GO3D", "new:snps-and-go3d", [SML]),
    "SPRI": ("spri", "SPRI", "new:spri", [SML]),
    "SaProt": ("saprot", "SaProt", UC + "saprot", [FM]),
    "SiPhy": ("siphy", "SiPHy", "brca-20261009-method-siphy", [SP]),
    "SuSPect": ("suspect", "SuSPect", "brca-20261009-method-suspect", [SML]),
    "TranceptEVE": ("trancepteve", "TranceptEVE", UC + "trancepteve", [SP]),
    "Tranception": ("tranception", "Tranception", UC + "tranception", [FM]),
    "UNEECON": ("uneecon", "UNEECON", "new:uneecon", [SP]),
    "Unirep_evotune": ("unirep-evotune", "Unirep (evotuned)", UC + "unirep-evotuned", [FM]),
    "VARITY_ER": ("varity-er", "VARITY (_R and _ER models)", SO + "varity", [SML]),
    "VARITY_R": ("varity-r", "VARITY (_R and _ER models)", SO + "varity", [SML]),
    "VESPA": ("vespa", "VESPA", UC + "vespa", [SML]),
    "VESPAl": ("vespal", "VESPAl", UC + "vespal", [SML]),
    "VEST4": ("vest4", "VEST4", SO + "vest4", [SML]),
    "Wavenet": ("wavenet", "Wavenet", UC + "wavenet", [SP]),
    "fathmm-MKL": ("fathmm-mkl", "Fathmm-MKL", SO + "fathmm-mkl", [SML]),
    "fitCons": ("fitcons", "fitCons", SO + "integrated-fitcons", [SP]),
    "gMVP": ("gmvp", "gMVP", SO + "gmvp", [SML]),
    "iGEMME": ("igemme", "iGEMME", "new:igemme", [SP]),
    "mutationTCN": ("mutationtcn", "mutationTCN", "new:mutationtcn", [SP]),
    "mvPPT": ("mvppt", "mvPPT", "new:mvppt", [SML]),
    "phastCons": ("phastcons", "phastCons", SO + "phastcons", [SP]),
    "phyloP": ("phylop", "phyloP", SO + "phylop", [SP]),
    "popEVE": ("popeve", "popEVE", SO + "popeve", [SP]),
    "sequence_unet": ("sequence-unet", "Sequence UNET", "new:sequence-unet", [SP]),
}
# Table S8 prints these labels for tools that Table S3 prints under another label.
S8_ALIAS = {"CPT": "CPT-1", "fathmm-XF": "FathmmXF"}
assert S3_NAMES <= set(VEP), S3_NAMES - set(VEP)
assert {S8_ALIAS.get(n, n) for n in S8_NAMES} <= set(VEP)
for name, (_s, s2label, _t, _m) in VEP.items():
    assert s2label is None or s2label in S2, (name, s2label)

# New method records: display name, AVE-independent description built only from Livesey and Marsh 2025.
NEW_METHODS = {
    "3cnet": "3Cnet", "alphscore": "AlphScore", "capice": "CAPICE", "cosmis": "COSMIS", "cpt": "CPT",
    "demask": "DeMaSk", "deepsav": "DeepSAV", "envision": "Envision", "inmerf": "InMeRF", "lassie": "LASSIE",
    "mistic": "MISTIC", "moi-pred": "MOI-Pred", "maverick": "Maverick", "phact": "PHACT", "phd-snp": "PhD-SNP",
    "rhapsody": "Rhapsody", "sigma": "SIGMA", "snpred": "SNPred", "snps-and-go": "SNPs&GO",
    "snps-and-go3d": "SNPs&GO3D", "spri": "SPRI", "uneecon": "UNEECON", "igemme": "iGEMME",
    "mutationtcn": "mutationTCN", "mvppt": "mvPPT", "sequence-unet": "Sequence UNET",
}
TYPE_TEXT = {
    "Clinical-trained": "clinical-trained (trained on human variants with clinical labels, or using a predictor that was)",
    "Clinical-trained,": "clinical-trained (trained on human variants with clinical labels, or using a predictor that was)",
    "Population-tuned": "population-tuned (not trained on clinical labels but exposed to human population data through tuning, optimisation or scaling)",
    "Population-free": "population-free (not trained using any human population data)",
}


def target_id(target):
    return f"{P}-method-{target[4:]}" if target.startswith("new:") else target


# ---------------------------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------------------------
add({
    "id": S_ART, "kind": "source",
    "name": "Livesey and Marsh 2025, Genome Biology 26:104 (Europe PMC full text XML)",
    "description": "Benchmark of 97 missense variant effect predictors against 36 human deep mutational scanning datasets, and of 83 predictors on ClinVar pathogenic versus gnomAD missense variants.",
    "status": "needs_review", "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": ["research", "clinical_research"]},
    "source_ids": [], "links": [],
    "attributes": {
        "url": ART["xml"][2], "version": "PMC12016141 (published 2025-04-22; Genome Biol 26:104)",
        "doi": "10.1186/s13059-025-03575-w", "retrieved_at": ART["xml"][3], "artifact_sha256": ART["xml"][1],
        "publication_status": "peer_reviewed", "licence": "CC BY 4.0", "media_type": "application/xml",
        "source_locator": "Results; Methods 'Spearman's correlation and rank score', 'AUROC and AUPRC', 'ClinVar and gnomAD data', 'DMS datasets', 'VEPs'; Tables 1-3; Data availability",
        "limitations": [
            "Figures 1-4 print no values; per-VEP results come from Supplementary Material 2.",
            "The authors obtained predictions for 27 VEPs from dbNSFP 4.2 and the rest from pre-calculated downloads, web servers, local runs or the ProteinGym website (Methods, 'VEPs').",
        ],
        "review": doc_review("xml", "Identity, version, licence and the methods text used for protocol descriptions read from the XML."),
    },
})
add({
    "id": S_SUPP, "kind": "source",
    "name": "Livesey and Marsh 2025, Supplementary Material 2 (Tables S1-S8)",
    "description": "Excel workbook with the DMS dataset list, VEP list and types, full pairwise win-rate matrices and rank scores for the DMS and clinical benchmarks, bootstrap counts and sensitivity analyses.",
    "status": "needs_review", "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": ["research", "clinical_research"]},
    "source_ids": [S_ART], "links": [],
    "attributes": {
        "url": ART["supp"][2], "version": "13059_2025_3575_MOESM2_ESM.xlsx as published with PMC12016141",
        "doi": "10.1186/s13059-025-03575-w", "retrieved_at": ART["supp"][3], "artifact_sha256": ART["supp"][1],
        "publication_status": "peer_reviewed", "licence": "CC BY 4.0 (article licence; the workbook carries no separate licence)",
        "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "source_locator": "Sheets 'Legends', 'Table S1' to 'Table S8', 'References'",
        "limitations": [
            "All numeric cells use the General number format; values are stored at up to 17 significant digits and printed_value records the shortest round-trip decimal of each stored number.",
            "Table S1 has no row 3 and leaves the fitness assay blank for TPK1, SUMO1, UBE2I and CASP7, so the direct and indirect assay groups cannot be counted from it.",
            "Table S2 has 93 rows for 97 benchmarked VEPs: BayesDel, EVmutation, PolyPhen-2 and VARITY rows each cover two scored variants.",
            "Table S8 prints 'CADD' and 'COSMIS', which have no row in Table S2, and 'CPT' and 'fathmm-XF' where Tables S2 and S3 print 'CPT-1' and 'Fathmm-XF'/'FathmmXF'.",
        ],
        "review": doc_review("supp", "Sheet names, headers and legends read from the workbook."),
    },
})
PG_SOURCE_TEXT = {
    "pg_dms": ("ProteinGym zero-shot DMS substitutions Spearman summary at commit 144fe22",
               "Official ProteinGym leaderboard file: average Spearman over 217 DMS substitution assays for 97 zero-shot models, with function, MSA-depth, taxon and mutational-depth breakdowns and a bootstrap standard error.",
               "benchmarks/DMS_zero_shot/substitutions/Spearman/Summary_performance_DMS_substitutions_Spearman.csv"),
    "pg_czs": ("ProteinGym clinical zero-shot substitutions AUC summary at commit 144fe22",
               "Official ProteinGym summary file: average AUC on the clinical substitution benchmark for 13 zero-shot models and unsupervised clinical predictors.",
               "benchmarks/clinical_zero_shot/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv"),
    "pg_css": ("ProteinGym clinical supervised substitutions AUC summary at commit 144fe22",
               "Official ProteinGym summary file: average AUC on the clinical substitution benchmark for 17 supervised clinical predictors.",
               "benchmarks/clinical_supervised/substitutions/AUC/Summary_performance_clinical_substitutions_AUC.csv"),
    "pg_czi": ("ProteinGym clinical zero-shot indels AUC summary at commit 144fe22",
               "Official ProteinGym summary file: average AUC on the clinical indel benchmark for 18 zero-shot models.",
               "benchmarks/clinical_zero_shot/indels/AUC/Summary_performance_clinical_indels_AUC.csv"),
}
for key, (name, desc, path) in PG_SOURCE_TEXT.items():
    lims = ["Mutable repository: the file is pinned to commit 144fe22b07dfaeec2b366f2346203a9838a55b4c, which was the head of main at retrieval (committed 2026-03-25).",
            "The repository does not record which script run, data release or model-score snapshot produced this file; the README says these summary files are what the website hosts."]
    if key == "pg_czs":
        lims.append("The header repeats 'Model_rank' and the second 'Model_rank' column is empty on every row.")
        lims.append("The file lists 13 models, far fewer than the zero-shot DMS file; the repository does not say whether the clinical summary is partial.")
    add({
        "id": S_PG[key], "kind": "source", "name": name, "description": desc,
        "status": "needs_review", "facets": {"areas": ["proteins-complexes"], "contexts": ["research"] if key == "pg_dms" else ["clinical_research"]},
        "source_ids": [], "links": [],
        "attributes": {
            "url": PG_BLOB + path, "artifact_url": ART[key][2], "version": PG_COMMIT,
            "retrieved_at": ART[key][3], "artifact_sha256": ART[key][1],
            "publication_status": "official_project_source", "licence": "MIT (repository LICENSE); underlying assay and clinical data carry their own terms",
            "media_type": "text/csv", "source_locator": path, "limitations": lims,
            "review": doc_review(key, "Header and row labels read from the CSV."),
        },
    })

# ---------------------------------------------------------------------------------------------
# New method records
# ---------------------------------------------------------------------------------------------
for printed, (cslug, s2label, target, mtypes) in VEP.items():
    if not target.startswith("new:"):
        continue
    mslug = target[4:]
    name = NEW_METHODS[mslug]
    if s2label:
        info = S2[s2label]
        desc = (f"Missense variant effect predictor. Livesey and Marsh 2025 class it as {TYPE_TEXT[info['type']]} "
                f"and obtained its predictions from {info['source']} (Table S2).")
        locator = f"Supplementary Material 2, Table S2 row {info['row']} ('{s2label}')"
        src = [S_SUPP, S_ART]
    else:
        desc = ("Missense variant effect predictor scored in the clinical ranking of Livesey and Marsh 2025 (Table S8, row 'COSMIS'). "
                "The paper's VEP list (Table S2) and text do not describe it.")
        locator = "Supplementary Material 2, Table S8 column A ('COSMIS')"
        src = [S_SUPP]
    if any(r["id"] == f"{P}-method-{mslug}" for r in records):
        continue
    add({
        "id": f"{P}-method-{mslug}", "kind": "method", "name": name, "description": desc,
        "status": "needs_review",
        "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": ["research", "clinical_research"], "method_types": mtypes},
        "source_ids": src, "links": [],
        "attributes": {
            "reported_name": name, "entity_level": "method", "source_locator": locator,
            "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; score versions are on configurations"}},
            "review": doc_review("supp", "Name and type transcribed from Table S2 (or Table S8 for COSMIS)."),
        },
    })

# ---------------------------------------------------------------------------------------------
# Livesey and Marsh 2025: benchmark, datasets, protocols, configurations
# ---------------------------------------------------------------------------------------------
BENCH = add({
    "id": f"{P}-benchmark-livesey-marsh-vep", "kind": "benchmark",
    "name": "Livesey and Marsh variant effect predictor benchmark (2025 edition)",
    "description": "Ranks missense variant effect predictors by pairwise comparisons of their Spearman correlation with human deep mutational scanning data, and separately by pairwise AUROC on ClinVar pathogenic versus gnomAD missense variants.",
    "status": "needs_review", "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": ["research", "clinical_research"]},
    "source_ids": [S_ART, S_SUPP], "links": [],
    "attributes": {
        "entity_level": "suite", "version": "Genome Biol 2025;26:104 (third edition, after Mol Syst Biol 2020 and 2023)",
        "task": "Missense variant effect prediction, ranked against functional assays and clinical labels",
        "scope_note": "97 VEPs on 36 human DMS datasets (one score set per protein, at least 1000 single amino acid substitutions after removing ClinVar and gnomAD variants); 83 VEPs on 819 proteins with at least 10 ClinVar pathogenic or likely pathogenic and 10 gnomAD v4.1 missense variants. Rank score is each VEP's average pairwise win rate against all other VEPs.",
        "source_locator": "Results 'New DMS datasets and VEPs', 'Comparison of VEP performance using DMS data', 'Performance of VEPs on clinical variant classification'; Methods",
        "limitations": [
            "Rank scores are relative: they depend on which other VEPs are in the comparison and are not a per-VEP correlation or AUROC.",
            "The earlier editions (Mol Syst Biol 2020;16:e9380 and 2023;19:e11474) used other DMS sets, VEP sets and, in 2020, another ranking method; they are not extracted here.",
        ],
        "review": doc_review("xml", "Scope read from Results and Methods."),
    },
})

D_DMS = add({
    "id": f"{P}-dataset-livesey2025-dms-36", "kind": "dataset",
    "name": "Livesey and Marsh 2025 human DMS benchmark set (36 proteins)",
    "description": "One deep mutational scanning score set per protein for 36 human proteins, with variants present in ClinVar or gnomAD removed.",
    "status": "needs_review", "facets": {"areas": ["proteins-complexes"], "contexts": ["research"]},
    "source_ids": [S_ART, S_SUPP], "links": [],
    "attributes": {
        "population": "36 human proteins, 207,460 single amino acid variants (Results). Per protein, the score set with the highest median Spearman correlation with all VEPs was chosen; datasets with fewer than 1000 scored substitutions after removing ClinVar and gnomAD variants, antibody-binding assays, the ACE2 to SARS-CoV-2 binding assay and datasets without methodological details were excluded. GCH1 is an unpublished dataset used with the authors' permission.",
        "variant_count": 207460,
        "split": "No training split; zero-shot comparison of VEP scores with DMS scores. For Envision, CPT-1, DeMaSk, VARITY_R and VARITY_ER the DMS sets used to train them are excluded from their comparisons (Table S2).",
        "assay": "Mixed: growth, complementation, binding, abundance (VAMP-seq), reporter and enzyme-activity assays, classed by the authors as direct or indirect (Table S1).",
        "species": "Homo sapiens",
        "access": "DMS and VEP predictions deposited at figshare doi:10.6084/m9.figshare.28295198 (Data availability); not retrieved in this pass.",
        "source_locator": "Results 'New DMS datasets and VEPs'; Methods 'DMS datasets'; Table 1; Supplementary Table S1; Data availability",
        "missing_metadata": {"version": {"reason": "unreported", "note": "No dataset version beyond the paper; the figshare deposit was not retrieved."}},
        "review": doc_review("xml", "Counts and selection rules read from Results and Methods."),
    },
})
D_CLIN = add({
    "id": f"{P}-dataset-livesey2025-clinvar-gnomad-819", "kind": "dataset",
    "name": "Livesey and Marsh 2025 clinical set: ClinVar pathogenic versus gnomAD v4.1 missense (819 proteins)",
    "description": "ClinVar pathogenic and likely pathogenic missense variants against 'putatively benign' gnomAD v4.1 missense variants, in proteins with at least 10 of each.",
    "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
    "source_ids": [S_ART], "links": [],
    "attributes": {
        "population": "819 human proteins with at least 10 pathogenic or likely pathogenic ClinVar missense variants (0-star and conflicting entries removed) and at least 10 gnomAD v4.1 missense variants that passed the genome or exome filters and were not classed pathogenic.",
        "label_semantics": "Positive: ClinVar pathogenic, likely pathogenic, pathogenic/likely pathogenic. Negative: gnomAD v4.1 missense variants, 'putatively benign', mostly rare; the authors note it will include some unclassified pathogenic variants, especially in recessive and incomplete-penetrance genes.",
        "split": "No held-out split; no variants used in VEP training were removed, so clinical-trained VEPs can benefit from circularity (Results).",
        "species": "Homo sapiens",
        "version": "ClinVar obtained 06/08/2024 (date format not stated); gnomAD v4.1",
        "access": "VEP predictions for these variants deposited at figshare doi:10.6084/m9.figshare.28295249 (Data availability); not retrieved in this pass.",
        "source_locator": "Methods 'ClinVar and gnomAD data'; Results 'Performance of VEPs on clinical variant classification'; Data availability",
        "review": doc_review("xml", "Label sources, filters and counts read from Methods and Results."),
    },
})

RANK_AGG = "Win rate of each VEP pair across proteins (wins divided by times the pair was tested), averaged over all other VEPs (Methods, 'Spearman's correlation and rank score')"
DMS_METRIC_IMPL = "scipy.stats.spearmanr (scipy 1.5.4, Python 3.6.8); absolute Spearman; the VEP with the higher |rho| on variants scored by the DMS and both VEPs earns the point"
LM_PROTOCOLS = {
    "dms-all": dict(
        name="Livesey and Marsh 2025 DMS benchmark: pairwise |Spearman| win rate, all 36 DMS sets",
        desc="Rank score of each VEP against 96 others on 36 human DMS datasets (Table S3 rank_score).",
        table="Table S3", data=D_DMS, ctx="research",
        scope="For each protein, every pair of VEPs is compared on the variants scored by the DMS and both VEPs; the VEP with the higher absolute Spearman correlation with the DMS scores wins. Each VEP's win rate against each other VEP across proteins is averaged into a rank score (0 to 100). The top_5_winrate column gives the same average restricted to the top five ranked VEPs.",
        qual="average pairwise win rate against all other VEPs, |Spearman| with DMS on shared variants, 36 human DMS sets",
    ),
    "dms-direct": dict(
        name="Livesey and Marsh 2025 DMS benchmark: pairwise |Spearman| win rate, direct assays only",
        desc="Rank score recalculated using only the DMS assays the authors class as direct (Table S5 rank_score_direct).",
        table="Table S5", data=D_DMS, ctx="research",
        scope="Same pairwise procedure as the main DMS ranking, restricted to direct assays: those that directly measure the ability of the target protein to carry out one or more functions (for example one- and two-hybrid assays and VAMP-seq).",
        qual="average pairwise win rate against all other VEPs, |Spearman| with DMS on shared variants, direct DMS assays only",
    ),
    "dms-indirect": dict(
        name="Livesey and Marsh 2025 DMS benchmark: pairwise |Spearman| win rate, indirect assays only",
        desc="Rank score recalculated using only the DMS assays the authors class as indirect (Table S5 rank_score_indirect).",
        table="Table S5", data=D_DMS, ctx="research",
        scope="Same pairwise procedure as the main DMS ranking, restricted to indirect assays, most commonly growth-rate experiments where the measured attribute is not directly controlled by the target protein.",
        qual="average pairwise win rate against all other VEPs, |Spearman| with DMS on shared variants, indirect DMS assays only",
    ),
    "dms-snv": dict(
        name="Livesey and Marsh 2025 DMS benchmark: pairwise |Spearman| win rate, SNV-accessible substitutions only",
        desc="Rank score recalculated on amino acid substitutions possible by a single nucleotide change (Table S6).",
        table="Table S6", data=D_DMS, ctx="research",
        scope="Same pairwise procedure as the main DMS ranking, restricted to substitutions possible by a single nucleotide variant, to reduce the effect of VEPs that cannot score multinucleotide changes.",
        qual="average pairwise win rate against all other VEPs, |Spearman| with DMS on shared variants, SNV-accessible substitutions only",
    ),
    "dms-snv-filled": dict(
        name="Livesey and Marsh 2025 DMS benchmark: pairwise |Spearman| win rate, SNV-accessible substitutions with gaps filled",
        desc="Rank score on SNV-accessible substitutions with each VEP's missing predictions filled with its most benign score (Table S7).",
        table="Table S7", data=D_DMS, ctx="research",
        scope="Same pairwise procedure as the main DMS ranking, restricted to SNV-accessible substitutions, with every remaining missing prediction filled with the most benign score that VEP produces.",
        qual="average pairwise win rate against all other VEPs, |Spearman| with DMS, SNV-accessible substitutions, missing predictions filled with the VEP's most benign score",
    ),
    "clinical-auroc": dict(
        name="Livesey and Marsh 2025 clinical benchmark: pairwise AUROC win rate, ClinVar pathogenic versus gnomAD missense",
        desc="Rank score of each VEP from per-protein pairwise AUROC comparisons on 819 proteins (Table S8 rank_score).",
        table="Table S8", data=D_CLIN, ctx="clinical_research",
        scope="For each protein with at least 10 ClinVar pathogenic or likely pathogenic and 10 gnomAD v4.1 missense variants, the AUROC of each pair of VEPs is compared on variants scored by both; the higher AUROC wins. Win rates across proteins are averaged over all other VEPs. No training variants were removed, so clinical-trained VEPs can benefit from circularity.",
        qual="average pairwise win rate against all other VEPs, per-protein AUROC on shared variants, ClinVar P/LP versus gnomAD v4.1 missense, proteins with at least 10 of each",
    ),
}
for pslug, spec in LM_PROTOCOLS.items():
    clinical = pslug == "clinical-auroc"
    spec["id"] = f"{P}-protocol-livesey2025-{pslug}"
    lims = [
        "A rank score is relative to the other VEPs in the same table; values from different tables or editions are not comparable.",
        "Per-pair, per-protein correlations and AUROCs behind the win rates are not printed; they are in the figshare deposit, which was not retrieved.",
    ]
    if clinical:
        lims += [
            "Clinical-trained VEPs were not filtered for training overlap; the authors attribute most of their advantage here to circularity (Results, Fig. 4).",
            "Figure 3 error bars are the standard error across comparisons; they are not printed.",
        ]
    else:
        lims += [
            "DMS assays measure a cellular or molecular phenotype chosen per protein, not pathogenicity.",
            "Figure 2 error bars (standard deviation over 1000 bootstraps of the DMS sets) are not printed; Table S4 gives pairwise bootstrap counts, not extracted.",
            "Five VEPs (Envision, CPT-1, DeMaSk, VARITY_R, VARITY_ER) have DMS sets they were trained on excluded, so they are compared on fewer proteins.",
        ]
    add({
        "id": spec["id"], "kind": "protocol", "name": spec["name"], "description": spec["desc"],
        "status": "needs_review", "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": [spec["ctx"]]},
        "source_ids": [S_ART, S_SUPP],
        "links": [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": spec["data"]}],
        "attributes": {
            "scope_note": spec["scope"],
            "task": "Clinical variant classification ranking" if clinical else "Missense variant effect prediction ranked against DMS",
            "metric": "pairwise-win-rate", "metric_direction": "higher", "unit": "percent",
            "metric_qualifier": spec["qual"],
            "metric_implementation": ("sklearn.metrics.roc_auc_score (sklearn 0.18.1); scores of VEPs where low means pathogenic are inverted by subtracting from 1; the higher AUROC on shared variants earns the point"
                                      if clinical else DMS_METRIC_IMPL),
            "aggregation": RANK_AGG,
            "version": f"Livesey and Marsh 2025, Supplementary Material 2 {spec['table']}",
            "publication_status": "peer_reviewed",
            "source_locator": f"Methods 'Spearman's correlation and rank score' and 'AUROC and AUPRC'; Supplementary Material 2 Legends ({spec['table']})",
            "limitations": lims,
            "review": doc_review("xml", "Procedure read from Methods and Results; table legend read from the workbook."),
        },
    })

CFG = {}


def vep_config(printed):
    cslug, s2label, target, mtypes = VEP[printed]
    cid = f"{P}-config-livesey2025-{cslug}"
    if cid in CFG:
        return cid
    attrs = {
        "reported_name": printed, "foundation_model_eligible": FM in mtypes,
        "configuration_type": "paper_evaluation",
    }
    missing = {}
    if s2label:
        info = S2[s2label]
        src = info["source"]
        if src == "dbNSFP":
            attrs["version"] = "dbNSFP 4.2 (Table S2 'Source'; Methods 'VEPs')"
        elif src == "ProteinGym":
            attrs["version"] = "Predictions from the ProteinGym website (Table S2 'Source'); ProteinGym release not stated"
        else:
            attrs["version"] = f"Predictions obtained from {src} (Table S2 'Source'); release not stated"
        attrs["training_overlap"] = f"Livesey and Marsh 2025 type: {info['type'].rstrip(',')}" + (
            f"; DMS sets used for training, excluded from its DMS comparisons: {info['dms_training']}" if info["dms_training"] else "")
        attrs["access_reuse"] = f"Livesey and Marsh obtained predictions from: {src}"
        attrs["source_locator"] = f"Supplementary Material 2, Table S2 row {info['row']} ('{s2label}'); printed label '{printed}' in Tables S3 and S5-S8"
        src_ids = [S_SUPP, S_ART]
    else:
        missing["version"] = {"reason": "unreported", "note": f"Table S8 prints '{printed}' and Table S2 has no row for it" + (
            "; Table S2 lists CADD 1.6 (dbNSFP) and CADD 1.7 (download) separately and Table S8 also prints CADD_1.7" if printed == "CADD" else "")}
        missing["training_overlap"] = {"reason": "unreported", "note": "Not classed in Table S2"}
        attrs["source_locator"] = f"Supplementary Material 2, Table S8 column A ('{printed}')"
        src_ids = [S_SUPP]
    if FM in mtypes or s2label in ("ProGen2", "RITA", "CARP", "ESM2", "ESM-1v", "Tranception", "TranceptEVE", "MSA Transformer"):
        missing["checkpoint"] = {"reason": "unreported", "note": "Model size or checkpoint not stated in the paper"}
    if missing:
        attrs["missing_metadata"] = missing
    attrs["review"] = doc_review("supp", "Label, type and prediction source transcribed from Tables S2, S3 and S8.")
    add({
        "id": cid, "kind": "configuration", "name": f"{printed} (Livesey and Marsh 2025)",
        "description": f"{printed} as scored in the Livesey and Marsh 2025 VEP benchmark.",
        "status": "needs_review",
        "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": ["research", "clinical_research"], "method_types": mtypes},
        "source_ids": src_ids, "links": [{"relation": "configuration_of", "target_id": target_id(target)}],
        "attributes": attrs,
    })
    CFG[cid] = printed
    return cid


def lm_eval(printed, pslug):
    spec = LM_PROTOCOLS[pslug]
    cid = vep_config(printed)
    clinical = pslug == "clinical-auroc"
    eid = f"{P}-eval-livesey2025-{pslug}-{VEP[printed][0]}"
    s2label = VEP[printed][1]
    inputs = (f"{printed} predictions from {S2[s2label]['source']}" if s2label else f"{printed} predictions (source not stated)")
    add({
        "id": eid, "kind": "evaluation", "name": f"{printed}: {spec['name']}",
        "description": "Independent benchmark by Livesey and Marsh 2025; transcribed, not reproduced.",
        "status": "needs_review", "facets": {"areas": ["dna-genomes", "proteins-complexes"], "contexts": [spec["ctx"]]},
        "source_ids": [S_SUPP, S_ART],
        "links": [{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": spec["id"]},
                  {"relation": "data", "target_id": spec["data"]}],
        "attributes": {
            "origin": "independent_paper",
            "protocol": spec["name"],
            "comparison": {
                "protocol_id": spec["id"],
                "dataset_version": ("ClinVar 06/08/2024 and gnomAD v4.1, 819 proteins" if clinical else "36 human DMS sets of Table S1"),
                "split": None,
                "population": ("Proteins with at least 10 ClinVar P/LP and 10 gnomAD missense variants; variants scored by both VEPs of a pair"
                               if clinical else "Variants scored by the DMS and both VEPs of a pair; ClinVar and gnomAD variants removed"),
                "inputs": inputs,
                "adaptation": "None; precomputed or locally run predictions",
                "metric_implementation": ("sklearn roc_auc_score (0.18.1) per protein" if clinical else DMS_METRIC_IMPL),
                "aggregation": RANK_AGG,
                "budget": None,
            },
            "source_locator": f"Supplementary Material 2, {spec['table']}, row '{printed}'",
            "missing_metadata": {"split": {"reason": "inapplicable", "note": "Zero-shot comparison with no training split"},
                                 "budget": {"reason": "unreported"}},
            "review": review("supp", "Row read by extract/extract_vep.py from the pinned workbook.", "Extracted, not reviewed."),
        },
    })
    return eid


def lm_result(eid, printed, pslug, metric_label, cell, qualifier, coverage=None):
    ref, raw = cell
    spec = LM_PROTOCOLS[pslug]
    rid = f"{eid.replace('-eval-', '-result-')}-{slug(metric_label)}"
    printed_value = short_decimal(raw)
    attrs = {
        "metric": "pairwise-win-rate", "metric_direction": "higher", "unit": "percent",
        "metric_qualifier": qualifier,
        "printed_value": printed_value, "numeric_value": printed_value,
        "raw_xml_value": raw, "workbook_number_format": "General",
        "source_locator": f"Supplementary Material 2, sheet '{spec['table']}', cell {ref} (row '{printed}', column '{metric_label}')",
        "missing_metadata": {"uncertainty": {"reason": "unreported", "note": ("Figure 3 error bars (standard error across comparisons) are not printed"
                                                                             if pslug == "clinical-auroc" else
                                                                             "Bootstrap standard deviations appear only as Figure 2 error bars; not printed")}},
        "review": review("supp", f"Read sheet '{spec['table']}' with a stdlib OOXML reader (extract/ooxml.py); header row and the full set of VEP labels asserted; printed_value is the shortest round-trip decimal of the stored General-format number.",
                         "Extracted, not reviewed. The review-evidence pass must re-check this cell against the pinned workbook."),
    }
    if coverage:
        attrs["coverage"] = coverage
    if printed in S8_ALIAS and pslug == "clinical-auroc":
        attrs["source_anomaly"] = f"Table S8 prints '{printed}'; mapped to the configuration printed '{S8_ALIAS[printed]}' in Tables S2 and S3."
    add({
        "id": rid, "kind": "result", "name": f"{printed} {metric_label} ({spec['table']})",
        "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        "status": "needs_review", "facets": {}, "source_ids": [S_SUPP, S_ART],
        "links": [{"relation": "evaluation", "target_id": eid}], "attributes": attrs,
    })
    claims_rows.append([rid, S_SUPP, attrs["source_locator"], printed_value, "result"])


def proteins_cov(cell, eligible, unit):
    ref, raw = cell
    n = int(float(raw))
    assert float(raw) == n
    return {"scored": n, "eligible": eligible, "unit": unit, "note": f"'proteins' column, cell {ref}"}


ALL_Q = LM_PROTOCOLS["dms-all"]["qual"]
for row in S3_ROWS:
    v = row["VEP"]
    eid = lm_eval(v, "dms-all")
    lm_result(eid, v, "dms-all", "rank_score", row["rank_score"], ALL_Q, proteins_cov(row["proteins"], 36, "human DMS datasets (one per protein) with predictions for this VEP"))
    lm_result(eid, v, "dms-all", "top_5_winrate", row["top_5_winrate"],
              "average pairwise win rate against the five top-ranked VEPs (column top_5_winrate; the five are not listed in the table), |Spearman| with DMS on shared variants, 36 human DMS sets")
for row in S5_ROWS:
    v = row["VEP"]
    for pslug, col in (("dms-direct", "rank_score_direct"), ("dms-indirect", "rank_score_indirect")):
        eid = lm_eval(v, pslug)
        lm_result(eid, v, pslug, col, row[col], LM_PROTOCOLS[pslug]["qual"])
for rows, pslug in ((S6_ROWS, "dms-snv"), (S7_ROWS, "dms-snv-filled")):
    for row in rows:
        v = row["VEP"]
        eid = lm_eval(v, pslug)
        lm_result(eid, v, pslug, "rank_score", row["rank_score"], LM_PROTOCOLS[pslug]["qual"],
                  proteins_cov(row["proteins"], 36, "human DMS datasets (one per protein) with predictions for this VEP"))
for row in S8_ROWS:
    v = row["VEP"]
    key = S8_ALIAS.get(v, v)
    eid = lm_eval(key, "clinical-auroc")
    lm_result(eid, v, "clinical-auroc", "rank_score", row["rank_score"], LM_PROTOCOLS["clinical-auroc"]["qual"],
              proteins_cov(row["proteins"], 819, "proteins with at least 10 ClinVar P/LP and 10 gnomAD missense variants scored by this VEP"))

# ---------------------------------------------------------------------------------------------
# ProteinGym summaries at 144fe22
# ---------------------------------------------------------------------------------------------
def read_csv(key):
    with open(paths[key], newline="") as fh:
        rows = list(csv.reader(fh))
    return rows[0], rows[1:]


pg_cfg = {}
for line in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "pg_configurations.tsv")):
    if line.startswith("#") or not line.strip():
        continue
    label, cid = line.rstrip("\n").split("\t")
    pg_cfg[label] = cid

D_PG = {
    "pg_dms": f"{P}-data-proteingym-dms-substitutions-144fe22",
    "pg_czs": f"{P}-data-proteingym-clinical-substitutions-144fe22",
    "pg_css": f"{P}-data-proteingym-clinical-substitutions-144fe22",
    "pg_czi": f"{P}-data-proteingym-clinical-indels-144fe22",
}
add({
    "id": D_PG["pg_dms"], "kind": "dataset_subset", "name": "ProteinGym DMS substitution assays at commit 144fe22 (217 assays)",
    "description": "The 217 deep mutational scanning substitution assays of the ProteinGym reference file at commit 144fe22 (v1.3), single and multiple substitutions.",
    "status": "needs_review", "facets": {"areas": ["proteins-complexes"], "contexts": ["research"]},
    "source_ids": [PG_REFERENCE_SOURCE, PG_README_SOURCE], "links": [],
    "attributes": {"assay_count": 217, "version": f"{PG_COMMIT} (README: latest version v1.3)",
                   "source_locator": "reference_files/DMS_substitutions.csv (217 data rows); README.md line 22",
                   "review": doc_review("pg_dms", "Assay count from the pinned reference file record already in the store; version from the README at the same commit.")},
})
add({
    "id": D_PG["pg_czs"], "kind": "dataset_subset", "name": "ProteinGym clinical substitution benchmark at commit 144fe22",
    "description": "ProteinGym clinical substitution variants (benign or pathogenic labels per protein); the README at this commit gives 2,525 clinical proteins.",
    "status": "needs_review", "facets": {"areas": ["proteins-complexes", "dna-genomes"], "contexts": ["clinical_research"]},
    "source_ids": [PG_README_SOURCE], "links": [],
    "attributes": {"version": PG_COMMIT, "subset_scope": "2,525 clinical proteins (README line 22); labels DMS_score_bin 1 pathogenic, 0 benign (README line 28). The README gives protein counts only, not variant counts.",
                   "source_locator": "README.md lines 22 and 28",
                   "review": doc_review("pg_czs", "Counts and label meaning read from the README at the same commit.")},
})
add({
    "id": D_PG["pg_czi"], "kind": "dataset_subset", "name": "ProteinGym clinical indel benchmark at commit 144fe22",
    "description": "ProteinGym clinical indel variants (benign or pathogenic labels per protein); the README at this commit gives 1,555 clinical proteins.",
    "status": "needs_review", "facets": {"areas": ["proteins-complexes", "dna-genomes"], "contexts": ["clinical_research"]},
    "source_ids": [PG_README_SOURCE], "links": [],
    "attributes": {"version": PG_COMMIT, "subset_scope": "1,555 clinical proteins (README line 22). The README gives protein counts only, not variant counts.",
                   "source_locator": "README.md line 22",
                   "review": doc_review("pg_czi", "Counts read from the README at the same commit.")},
})

PG_PROTOCOLS = {
    "pg_czs": dict(id=f"{P}-protocol-proteingym-clinical-zero-shot-substitutions-auc-144fe22",
                   name="ProteinGym clinical substitutions, zero-shot, average AUC (commit 144fe22)",
                   desc="Zero-shot models and unsupervised clinical predictors ranked by AUC for pathogenic versus benign clinical substitutions, averaged over proteins.",
                   task="Clinical substitution pathogenicity classification, zero-shot"),
    "pg_css": dict(id=f"{P}-protocol-proteingym-clinical-supervised-substitutions-auc-144fe22",
                   name="ProteinGym clinical substitutions, supervised predictors, average AUC (commit 144fe22)",
                   desc="Supervised clinical predictors from dbNSFP ranked by AUC for pathogenic versus benign clinical substitutions, averaged over proteins.",
                   task="Clinical substitution pathogenicity classification, supervised predictors"),
    "pg_czi": dict(id=f"{P}-protocol-proteingym-clinical-zero-shot-indels-auc-144fe22",
                   name="ProteinGym clinical indels, zero-shot, average AUC (commit 144fe22)",
                   desc="Zero-shot models ranked by AUC for pathogenic versus benign clinical indels, averaged over proteins.",
                   task="Clinical indel pathogenicity classification, zero-shot"),
}
for key, spec in PG_PROTOCOLS.items():
    lims = [
        "The README says per-protein AUC is the clinical metric and gives dbNSFP 4.4a as the source of clinical baselines; the script that wrote this summary file was not read, so the averaging and the bootstrap standard error are not verified for this file.",
        "Supervised clinical predictors were trained on clinical labels that may overlap the benchmark's variants; ProteinGym's summary does not remove them." if key == "pg_css" else
        "Clinical labels come from ClinVar-type assertions; overlap with any model's training data is not assessed in the file.",
        "Not comparable with the DMS summaries or with Livesey and Marsh's rank scores.",
    ]
    add({
        "id": spec["id"], "kind": "protocol", "name": spec["name"], "description": spec["desc"],
        "status": "needs_review", "facets": {"areas": ["proteins-complexes", "dna-genomes"], "contexts": ["clinical_research"]},
        "source_ids": [S_PG[key], PG_README_SOURCE],
        "links": [{"relation": "part_of", "target_id": PG_BENCHMARK}, {"relation": "uses_data", "target_id": D_PG[key]}],
        "attributes": {
            "task": spec["task"], "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
            "metric_qualifier": "Average_AUC column of the ProteinGym clinical summary file",
            "version": PG_COMMIT, "upstream_revision": PG_COMMIT, "publication_status": "official_project_source",
            "source_locator": f"{PG_SOURCE_TEXT[key][2]}; README.md lines 39-52 and 106",
            "limitations": lims,
            "review": doc_review(key, "Protocol described from the README and the file header."),
        },
    })

PG_DMS_COLS = [
    ("Average_Spearman", "mean over selection types of the per-type mean over proteins of assay-level Spearman (all 217 assays)", "Average_Spearman"),
    ("Function_Activity", "Activity assays: mean over proteins of assay-level Spearman", "Function_Activity"),
    ("Function_Binding", "Binding assays: mean over proteins of assay-level Spearman", "Function_Binding"),
    ("Function_Expression", "Expression assays: mean over proteins of assay-level Spearman", "Function_Expression"),
    ("Function_OrganismalFitness", "Organismal fitness assays: mean over proteins of assay-level Spearman", "Function_OrganismalFitness"),
    ("Function_Stability", "Stability assays: mean over proteins of assay-level Spearman", "Function_Stability"),
    ("Low_MSA_depth", "Low MSA depth proteins: mean over proteins of assay-level Spearman", "Low_MSA_depth"),
    ("Medium_MSA_depth", "Medium MSA depth proteins: mean over proteins of assay-level Spearman", "Medium_MSA_depth"),
    ("High_MSA_depth", "High MSA depth proteins: mean over proteins of assay-level Spearman", "High_MSA_depth"),
    ("Taxa_Human", "Human proteins: mean over proteins of assay-level Spearman", "Taxa_Human"),
    ("Taxa_Other_Eukaryote", "Other eukaryote proteins: mean over proteins of assay-level Spearman", "Taxa_Other_Eukaryote"),
    ("Taxa_Prokaryote", "Prokaryote proteins: mean over proteins of assay-level Spearman", "Taxa_Prokaryote"),
    ("Taxa_Virus", "Virus proteins: mean over proteins of assay-level Spearman", "Taxa_Virus"),
    ("Depth_1", "variants with 1 substitution: mean over protein and selection-type groups of assay-level Spearman", "Depth_1"),
    ("Depth_2", "variants with 2 substitutions: mean over protein and selection-type groups of assay-level Spearman", "Depth_2"),
    ("Depth_3", "variants with 3 substitutions: mean over protein and selection-type groups of assay-level Spearman", "Depth_3"),
    ("Depth_4", "variants with 4 substitutions: mean over protein and selection-type groups of assay-level Spearman", "Depth_4"),
    ("Depth_5+", "variants with 5 or more substitutions: mean over protein and selection-type groups of assay-level Spearman", "Depth_5plus"),
]
PG_AGG = ("Assay-level metrics rounded to 3 decimals; averaged over assays per UniProt ID and selection type, then over proteins within each selection type, "
          "then equally over the five selection types (performance_DMS_benchmarks.py lines 304-315); breakdown columns average per protein within the category (lines 336-348) "
          "or, for mutational depth, over protein and selection-type groups (lines 321-330)")

header, rows = read_csv("pg_dms")
assert header == ["Model_rank", "Model_name", "Model type", "Average_Spearman", "Bootstrap_standard_error_Spearman",
                  "Function_Activity", "Function_Binding", "Function_Expression", "Function_OrganismalFitness", "Function_Stability",
                  "Low_MSA_depth", "Medium_MSA_depth", "High_MSA_depth", "Taxa_Human", "Taxa_Other_Eukaryote", "Taxa_Prokaryote",
                  "Taxa_Virus", "Depth_1", "Depth_2", "Depth_3", "Depth_4", "Depth_5+", "Model details", "References"], header
assert len(rows) == 97, len(rows)
assert rows[0][1] == "AIDO Protein-RAG (16B)" and rows[0][4] == "0.0"
H = {h: i for i, h in enumerate(header)}
for line_no, row in enumerate(rows, start=2):
    label = row[H["Model_name"]]
    cid = pg_cfg[label]
    eid = f"{P}-eval-pg-dms-{cid.split('-config-')[-1]}"
    add({
        "id": eid, "kind": "evaluation", "name": f"{label}: ProteinGym zero-shot DMS substitutions summary (144fe22)",
        "description": "Official ProteinGym leaderboard summary row; transcribed, not reproduced.",
        "status": "needs_review", "facets": {"areas": ["proteins-complexes"], "contexts": ["research"]},
        "source_ids": [S_PG["pg_dms"], PG_SCRIPT_SOURCE],
        "links": [{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": PG_DMS_PROTOCOL},
                  {"relation": "data", "target_id": D_PG["pg_dms"]}],
        "attributes": {
            "origin": "author_reported",
            "protocol": "ProteinGym zero-shot DMS substitutions, Spearman summary",
            "input_information": f"ProteinGym 'Model type' label: {row[H['Model type']]}",
            "comparison": {
                "protocol_id": PG_DMS_PROTOCOL, "dataset_version": PG_COMMIT, "split": None,
                "population": "217 DMS substitution assays (single and multiple substitutions)",
                "inputs": f"ProteinGym model label '{label}', model type '{row[H['Model type']]}'",
                "adaptation": "Zero-shot; no assay labels used",
                "metric_implementation": "Spearman per assay (performance_DMS_benchmarks.py at 144fe22)",
                "aggregation": PG_AGG, "budget": None,
            },
            "source_locator": f"{PG_SOURCE_TEXT['pg_dms'][2]} line {line_no} (Model_rank {row[H['Model_rank']]})",
            "missing_metadata": {"split": {"reason": "inapplicable", "note": "Zero-shot track"},
                                 "per_model_scored_count": {"reason": "unreported", "note": "The summary file does not print how many assays each model scored"},
                                 "budget": {"reason": "unreported"}},
            "review": review("pg_dms", "Row read by extract/extract_vep.py with csv.reader from the pinned file.", "Extracted, not reviewed."),
        },
    })
    for col, qual, cslug in PG_DMS_COLS:
        value = row[H[col]]
        assert re.fullmatch(r"-?\d+\.\d+", value), (label, col, value)
        attrs = {
            "metric": "spearman-correlation", "metric_direction": "higher", "unit": "unitless",
            "metric_qualifier": f"ProteinGym zero-shot DMS substitutions, {qual}",
            "printed_value": value, "numeric_value": value,
            "source_locator": f"{PG_SOURCE_TEXT['pg_dms'][2]} line {line_no}, row '{label}', column '{col}'",
            "review": review("pg_dms", "csv.reader parse of the pinned file; header and 97 model labels asserted.",
                             "Extracted, not reviewed. The review-evidence pass must re-check this cell."),
        }
        if col == "Average_Spearman":
            se = row[H["Bootstrap_standard_error_Spearman"]]
            attrs["uncertainty"] = {
                "type": "standard_error", "value": se, "printed": se, "method": "bootstrap", "resamples": 10000,
                "scope": "Standard error of this model's difference from the top-ranked model's average (AIDO Protein-RAG (16B), printed 0.0), resampling protein and selection-type rows within each selection type",
                "source_column": "Bootstrap_standard_error_Spearman",
                "note": "From compute_bootstrap_standard_error_functional_categories in performance_DMS_benchmarks.py at 144fe22 (default 10,000 resamples, lines 95-111 and 310-315); not an absolute standard error of the model's own average.",
            }
        else:
            attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
        rid = f"{eid.replace('-eval-', '-result-')}-{slug(cslug)}"
        add({
            "id": rid, "kind": "result", "name": f"{label} {col} (ProteinGym 144fe22)",
            "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
            "status": "needs_review", "facets": {}, "source_ids": [S_PG["pg_dms"]],
            "links": [{"relation": "evaluation", "target_id": eid}], "attributes": attrs,
        })
        claims_rows.append([rid, S_PG["pg_dms"], attrs["source_locator"], value, "result"])

# Clinical summaries: configurations for labels without a ProteinGym configuration in the store.
PG_CLIN_NEW = {
    "EVE": ("eve", UC + "eve", [SP]), "Provean": ("provean", SO + "provean", [CP]), "SIFT": ("sift", SO + "sift", [CP]),
    "SIFT4G": ("sift4g", SO + "sift", [CP]), "MutationAssessor": ("mutationassessor", SO + "mutationassessor", [SP]),
    "MutPred": ("mutpred", SO + "mutpred", [SML]), "PrimateAI": ("primateai", SO + "primateai", [SML]),
    "LIST-S2": ("list-s2", SO + "list-s2", [SP]), "LRT": ("lrt", SO + "lrt", [SP]),
    "Hidden Markov Model": ("hidden-markov-model", f"{P}-method-proteingym-hmm", [CP]),
    "ClinPred": ("clinpred", SO + "clinpred", [SML]), "MetaRNN": ("metarnn", SO + "metarnn", [SML]),
    "BayesDel (addAF)": ("bayesdel-addaf", "uc-clinical-20260930-method-bayesdel", [SML]),
    "BayesDel (noAF)": ("bayesdel-noaf", "uc-clinical-20260930-method-bayesdel", [SML]),
    "VEST4": ("vest4", SO + "vest4", [SML]), "REVEL": ("revel", SO + "revel", [SML]),
    "VARITY (R)": ("varity-r", SO + "varity", [SML]), "VARITY (ER)": ("varity-er", SO + "varity", [SML]),
    "gMVP": ("gmvp", SO + "gmvp", [SML]), "CADD": ("cadd", SO + "cadd", [SML]),
    "PolyPhen2 (HVAR)": ("polyphen2-hvar", SO + "polyphen2", [SML]), "PolyPhen2 (HDIV)": ("polyphen2-hdiv", SO + "polyphen2", [SML]),
    "DEOGEN2": ("deogen2", SO + "deogen2", [SML]), "MPC": ("mpc", SO + "mpc", [SML]),
    "MutationTaster": ("mutationtaster", SO + "mutationtaster", [SML]), "DANN": ("dann", SO + "dann", [SML]),
    "FATHMM": ("fathmm", SO + "fathmm", [SP]),
}
add({
    "id": f"{P}-method-proteingym-hmm", "kind": "method", "name": "Profile hidden Markov model (ProteinGym baseline)",
    "description": "Alignment-based profile hidden Markov model baseline that ProteinGym labels 'Hidden Markov Model' in its clinical indel summary.",
    "status": "needs_review", "facets": {"areas": ["proteins-complexes"], "contexts": ["clinical_research"], "method_types": [CP]},
    "source_ids": [S_PG["pg_czi"]], "links": [],
    "attributes": {"reported_name": "Hidden Markov Model", "entity_level": "method",
                   "source_locator": "Summary_performance_clinical_indels_AUC.csv row 'Hidden Markov Model', Model type 'MSA'",
                   "missing_metadata": {"version": {"reason": "unreported", "note": "Implementation and settings not stated in the summary file"}},
                   "review": doc_review("pg_czi", "Label and model type read from the CSV; the HMM software is not named in the file.")},
})
pg_clin_cfg = {}


def pg_clin_config(label, model_type):
    if label in pg_cfg:
        return pg_cfg[label]
    if label in pg_clin_cfg:
        return pg_clin_cfg[label]
    cslug, target, mtypes = PG_CLIN_NEW[label]
    cid = f"{P}-config-proteingym-clinical-{cslug}"
    dbnsfp = model_type in ("Clinical Predictor", "Supervised")
    attrs = {"reported_name": label, "foundation_model_eligible": False, "configuration_type": "reported_configuration",
             "version": ("dbNSFP 4.4a scores (README line 106: clinical baselines from dbNSFP 4.4a); ProteinGym commit " + PG_COMMIT
                         if dbnsfp else f"ProteinGym commit {PG_COMMIT}, label '{label}'"),
             "access_reuse": "Scores distributed by ProteinGym (README 'Clinical Model scores' downloads); original tool terms apply",
             "source_locator": f"ProteinGym clinical summary CSVs at {PG_COMMIT}, Model_name '{label}', Model type '{model_type}'",
             "review": doc_review("pg_czs", "Label and model type read from the clinical summary CSVs; dbNSFP version from the README.")}
    if not dbnsfp:
        attrs["missing_metadata"] = {"checkpoint": {"reason": "unreported", "note": "The clinical summary does not say whether EVE is the single or ensemble configuration"}} if label == "EVE" else {
            "checkpoint": {"reason": "unreported"}}
    add({
        "id": cid, "kind": "configuration", "name": f"{label} [ProteinGym 144fe22 clinical summary]",
        "description": f"{label} as listed in the ProteinGym clinical benchmark summary at commit 144fe22.",
        "status": "needs_review",
        "facets": {"areas": ["proteins-complexes", "dna-genomes"], "contexts": ["clinical_research"], "method_types": mtypes},
        "source_ids": [S_PG["pg_czs"], S_PG["pg_css"], S_PG["pg_czi"], PG_README_SOURCE],
        "links": [{"relation": "configuration_of", "target_id": target}], "attributes": attrs,
    })
    pg_clin_cfg[label] = cid
    return cid


EXPECTED_CLIN = {"pg_czs": 13, "pg_css": 17, "pg_czi": 18}
for key in ("pg_czs", "pg_css", "pg_czi"):
    header, rows = read_csv(key)
    assert len(rows) == EXPECTED_CLIN[key], (key, len(rows))
    H = {}
    for i, h in enumerate(header):
        H.setdefault(h, i)
    has_se = "Bootstrap_standard_error_AUC" in H
    expected_header = {"pg_czs": ["Model_rank", "Model_rank", "Model_name", "Model type", "Average_AUC", "Bootstrap_standard_error_AUC"],
                       "pg_css": ["Model_rank", "Model_name", "Model type", "Average_AUC", "Bootstrap_standard_error_AUC"],
                       "pg_czi": ["Model_rank", "Model_name", "Model type", "Average_AUC"]}[key]
    assert header == expected_header, (key, header)
    spec = PG_PROTOCOLS[key]
    for line_no, row in enumerate(rows, start=2):
        label, mtype, auc = row[H["Model_name"]], row[H["Model type"]], row[H["Average_AUC"]]
        assert re.fullmatch(r"\d\.\d+", auc), (key, label, auc)
        cid = pg_clin_config(label, mtype)
        short = cid.split("-config-")[-1]
        eid = f"{P}-eval-{key.replace('_', '-')}-{short}"
        add({
            "id": eid, "kind": "evaluation", "name": f"{label}: {spec['name']}",
            "description": "Official ProteinGym summary row; transcribed, not reproduced.",
            "status": "needs_review", "facets": {"areas": ["proteins-complexes", "dna-genomes"], "contexts": ["clinical_research"]},
            "source_ids": [S_PG[key]],
            "links": [{"relation": "system", "target_id": cid}, {"relation": "assessment", "target_id": spec["id"]},
                      {"relation": "data", "target_id": D_PG[key]}],
            "attributes": {
                "origin": "author_reported", "protocol": spec["name"],
                "input_information": f"ProteinGym 'Model type' label: {mtype}",
                "comparison": {"protocol_id": spec["id"], "dataset_version": PG_COMMIT, "split": None, "population": None,
                               "inputs": f"ProteinGym label '{label}', model type '{mtype}'",
                               "adaptation": "Supervised clinical predictor scores from dbNSFP" if key == "pg_css" else "Zero-shot",
                               "metric_implementation": None, "aggregation": None, "budget": None},
                "source_locator": f"{PG_SOURCE_TEXT[key][2]} line {line_no}",
                "missing_metadata": {"metric_implementation": {"reason": "unextracted", "note": "Clinical scoring script not read"},
                                     "aggregation": {"reason": "unextracted", "note": "Clinical scoring script not read"},
                                     "split": {"reason": "inapplicable"}, "budget": {"reason": "unreported"}},
                "review": review(key, "Row read by extract/extract_vep.py with csv.reader from the pinned file.", "Extracted, not reviewed."),
            },
        })
        attrs = {
            "metric": "auroc", "metric_direction": "higher", "unit": "unitless",
            "metric_qualifier": {"pg_czs": "ProteinGym clinical substitutions, zero-shot, Average_AUC over proteins",
                                 "pg_css": "ProteinGym clinical substitutions, supervised clinical predictors, Average_AUC over proteins",
                                 "pg_czi": "ProteinGym clinical indels, zero-shot, Average_AUC over proteins"}[key],
            "printed_value": auc, "numeric_value": auc,
            "source_locator": f"{PG_SOURCE_TEXT[key][2]} line {line_no}, row '{label}', column 'Average_AUC'",
            "review": review(key, "csv.reader parse of the pinned file; header and row count asserted.",
                             "Extracted, not reviewed. The review-evidence pass must re-check this cell."),
        }
        if has_se:
            se = row[H["Bootstrap_standard_error_AUC"]]
            attrs["uncertainty"] = {"type": "unresolved_spread", "value": se, "printed": se, "source_column": "Bootstrap_standard_error_AUC",
                                    "note": "Labelled a bootstrap standard error. The script that wrote the clinical summary was not read; in the DMS script the same column is the standard error of the difference from the top model, and the top row here prints 0.0, which suggests the same construction. Not verified for this file."}
        else:
            attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
        rid = f"{eid.replace('-eval-', '-result-')}-average-auc"
        add({
            "id": rid, "kind": "result", "name": f"{label} Average_AUC ({spec['name']})",
            "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
            "status": "needs_review", "facets": {}, "source_ids": [S_PG[key]],
            "links": [{"relation": "evaluation", "target_id": eid}], "attributes": attrs,
        })
        claims_rows.append([rid, S_PG[key], attrs["source_locator"], auc, "result"])

# ---------------------------------------------------------------------------------------------
# Descriptive claim: what was not extracted from Livesey and Marsh 2025
# ---------------------------------------------------------------------------------------------
NOT_EXTRACTED = ("Not extracted as results: the pairwise win-rate matrix bodies of Tables S3 (97 x 97) and S8 (85 x 85), "
                 "kept only through each VEP's rank_score, proteins and top_5_winrate columns; Table S4 (bootstrap counts behind the Figure 2 error bars); "
                 "the absolute_difference column of Table S5 (a difference of two extracted values); Tables S1 and S2, used for dataset and configuration "
                 "descriptions; Figures 1-4 and Supplementary Figs. S1-S6 (no printed values; the AUPRC ranking of Fig. S5 is figure-only); "
                 "the figshare deposits of per-variant predictions and scripts.")
cid_claim = add({
    "id": f"{P}-claim-livesey2025-not-extracted", "kind": "claim", "name": f"tables_not_extracted: {S_SUPP}",
    "description": "Descriptive fact transcribed from the pinned source.", "status": "needs_review", "facets": {},
    "source_ids": [S_SUPP, S_ART], "links": [{"relation": "subject", "target_id": S_SUPP}],
    "attributes": {"field": "tables_not_extracted", "value": NOT_EXTRACTED,
                   "source_locator": "Supplementary Material 2 Legends and Tables S1-S8; Figures 1-4; Data availability",
                   "review": doc_review("supp", "Written by the collector from the workbook legends and the article.")},
})
claims_rows.append([cid_claim, S_SUPP, "Supplementary Material 2 Legends; Figures 1-4", NOT_EXTRACTED[:200], "claim"])

# ---------------------------------------------------------------------------------------------
# Use-case relevance judgements (needs_review). The assessed_by links go on the use cases at
# integration, through records -- change; see coverage.json.
# ---------------------------------------------------------------------------------------------
def evals_on(protocol_id):
    return sorted(r["id"] for r in records if r["kind"] == "evaluation"
                  and any(l["relation"] == "assessment" and l["target_id"] == protocol_id for l in r["links"]))


UC_RARE = "use-case-rare-disease-candidate-ranking"
UC_BRCA = "use-case-brca1-brca2-germline-interpretation"
UC_STAB = "use-case-protein-stability"
LM = {k: v["id"] for k, v in LM_PROTOCOLS.items()}
PG = {k: v["id"] for k, v in PG_PROTOCOLS.items()}
COMMON_LIMITS = ["Transcribed from the source; no reproduction by Rewire and no human scientific review."]
J = [
    (UC_RARE, LM["dms-all"], "proxy", "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "DMS benchmark, all 36 DMS sets", 1,
     "Average pairwise win rate of each missense VEP against 96 others, by |Spearman| with 36 human DMS datasets",
     "Proxy: tells a lab which missense predictors best order variant effects within a protein, which bears on the molecular-effect evidence used to rank candidate variants. It does not measure recovery of causal variants or genes, review effort, or performance on non-missense variants.",
     [S_SUPP, S_ART], "Supplementary Material 2 Table S3; Methods 'Spearman's correlation and rank score'",
     ["DMS phenotypes are chosen per protein and are not pathogenicity labels.", "Rank scores are relative to the VEP set compared; they are not a correlation and cannot be compared with other tables."]),
    (UC_RARE, LM["dms-direct"], "proxy", "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "DMS benchmark, direct assays only", 2,
     "Average pairwise win rate by |Spearman| with the DMS assays the authors class as direct",
     "Proxy, as for the all-assay ranking; a robustness check of the same comparison on direct functional assays.",
     [S_SUPP, S_ART], "Supplementary Material 2 Table S5; Results", ["Which assays are direct is not fully recoverable from Table S1 (four blank assay descriptions)."]),
    (UC_RARE, LM["dms-indirect"], "proxy", "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "DMS benchmark, indirect assays only", 3,
     "Average pairwise win rate by |Spearman| with the DMS assays the authors class as indirect",
     "Proxy, as for the all-assay ranking; a robustness check on indirect (mostly growth) assays.",
     [S_SUPP, S_ART], "Supplementary Material 2 Table S5; Results", ["Which assays are indirect is not fully recoverable from Table S1."]),
    (UC_RARE, LM["dms-snv"], "proxy", "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "DMS benchmark, SNV-accessible substitutions", 4,
     "Average pairwise win rate by |Spearman| restricted to substitutions reachable by one nucleotide change",
     "Proxy; the SNV restriction matches the variants a clinical exome or genome produces more closely than all 19 substitutions per site.",
     [S_SUPP, S_ART], "Supplementary Material 2 Table S6; Results", []),
    (UC_RARE, LM["dms-snv-filled"], "proxy", "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "DMS benchmark, SNV-accessible, gaps filled", 5,
     "Average pairwise win rate by |Spearman| on SNV-accessible substitutions with missing predictions set to each VEP's most benign score",
     "Proxy; penalises VEPs that leave regions unscored, which matters when a lab needs a score for every candidate.",
     [S_SUPP, S_ART], "Supplementary Material 2 Table S7; Results", []),
    (UC_RARE, LM["clinical-auroc"], "proxy", "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "Clinical benchmark, ClinVar P/LP versus gnomAD missense", 6,
     "Average pairwise win rate by per-protein AUROC separating ClinVar P/LP from gnomAD v4.1 missense variants in 819 proteins",
     "Proxy: per-protein discrimination of pathogenic from population missense variants is close to the within-gene prioritisation a rare-disease lab does, but it does not measure ranking of causal variants among a proband's candidates or review effort.",
     [S_SUPP, S_ART], "Supplementary Material 2 Table S8; Methods 'ClinVar and gnomAD data', 'AUROC and AUPRC'",
     ["No training variants were removed; clinical-trained VEPs are likely inflated by circularity (Results, Fig. 4).",
      "The negative class is gnomAD missense variants, not confirmed benign variants."]),
    (UC_RARE, PG["pg_czs"], "proxy", "auroc", "proteingym-clinical-144fe22", "ProteinGym clinical benchmark (commit 144fe22)", "Substitutions, zero-shot", 1,
     "Average over proteins of AUC separating pathogenic from benign clinical substitutions",
     "Proxy: pathogenic versus benign discrimination of clinical missense variants bears on variant prioritisation, without measuring causal-variant recovery in cases.",
     [S_PG["pg_czs"], PG_README_SOURCE], "Summary_performance_clinical_substitutions_AUC.csv (zero-shot); README lines 22-28, 106",
     ["Only 13 models are listed; the file's completeness is not stated.", "Averaging and uncertainty construction not verified for the clinical summaries."]),
    (UC_RARE, PG["pg_css"], "proxy", "auroc", "proteingym-clinical-144fe22", "ProteinGym clinical benchmark (commit 144fe22)", "Substitutions, supervised predictors", 2,
     "Average over proteins of AUC for supervised clinical predictors from dbNSFP 4.4a",
     "Proxy, as for the zero-shot clinical summary; supervised predictors were trained on clinical labels.",
     [S_PG["pg_css"], PG_README_SOURCE], "Summary_performance_clinical_substitutions_AUC.csv (supervised); README line 106",
     ["Training-label overlap with the benchmark is not removed, so supervised scores can be inflated by circularity.",
      "Do not compare with the zero-shot rows as if on equal footing."]),
    (UC_RARE, PG["pg_czi"], "proxy", "auroc", "proteingym-clinical-144fe22", "ProteinGym clinical benchmark (commit 144fe22)", "Indels, zero-shot", 3,
     "Average over proteins of AUC separating pathogenic from benign clinical indels",
     "Proxy: indel pathogenicity discrimination bears on prioritising in-frame and frameshift candidates, which most missense predictors cannot score.",
     [S_PG["pg_czi"], PG_README_SOURCE], "Summary_performance_clinical_indels_AUC.csv; README line 22", ["No uncertainty column in this file."]),
    (UC_BRCA, LM["clinical-auroc"], "proxy", "pairwise-win-rate", "livesey-marsh-2025-vep-ranking", "Livesey and Marsh 2025 VEP rankings", "Clinical benchmark, ClinVar P/LP versus gnomAD missense", 1,
     "Average pairwise win rate by per-protein AUROC, ClinVar P/LP versus gnomAD v4.1 missense, 819 proteins",
     "Proxy: informs which computational predictors discriminate pathogenic missense variants across genes, relevant to choosing a PP3/BP4 tool, but it is pan-gene, not BRCA1/BRCA2-specific, and not a classification under the ENIGMA specification.",
     [S_SUPP, S_ART], "Supplementary Material 2 Table S8; Methods",
     ["Whether BRCA1 or BRCA2 is among the 819 proteins is not stated in the extracted tables.", "No calibration to ACMG/AMP evidence strength.",
      "Clinical-trained VEPs likely inflated by circularity."]),
    (UC_BRCA, PG["pg_czs"], "proxy", "auroc", "proteingym-clinical-144fe22", "ProteinGym clinical benchmark (commit 144fe22)", "Substitutions, zero-shot", 1,
     "Average over proteins of AUC, pathogenic versus benign clinical substitutions",
     "Proxy: pan-gene discrimination of clinical missense variants; not BRCA-specific and not calibrated to evidence strength.",
     [S_PG["pg_czs"], PG_README_SOURCE], "Summary_performance_clinical_substitutions_AUC.csv (zero-shot)", ["Only 13 models listed."]),
    (UC_BRCA, PG["pg_css"], "proxy", "auroc", "proteingym-clinical-144fe22", "ProteinGym clinical benchmark (commit 144fe22)", "Substitutions, supervised predictors", 2,
     "Average over proteins of AUC for supervised clinical predictors (dbNSFP 4.4a), including REVEL and BayesDel",
     "Proxy: covers the predictors most often used for PP3/BP4 (REVEL, BayesDel), pan-gene; not BRCA-specific.",
     [S_PG["pg_css"], PG_README_SOURCE], "Summary_performance_clinical_substitutions_AUC.csv (supervised)",
     ["Supervised predictors' training labels overlap ClinVar; circularity is not controlled."]),
    (UC_STAB, PG_DMS_PROTOCOL, "proxy", "spearman-correlation", "proteingym-dms-144fe22", "ProteinGym zero-shot DMS substitutions (commit 144fe22)", "Function_Stability breakdown", 1,
     "Function_Stability column: mean over proteins of assay-level Spearman on ProteinGym stability assays",
     "Proxy: the stability breakdown ranks zero-shot models by agreement with experimental stability assays, which bears directly on choosing a stability ranking method; the headline average mixes in activity, binding, expression and fitness assays and should not be used for this question.",
     [S_PG["pg_dms"], PG_SCRIPT_SOURCE], "Summary_performance_DMS_substitutions_Spearman.csv column Function_Stability; performance_DMS_benchmarks.py lines 336-348",
     ["Use only results whose metric_qualifier names Stability assays.", "Assays include multiple substitutions; Depth_1 is the singles-only column but is not stability-specific.",
      "The stability assays are mostly one high-throughput proteolysis study; the number of stability assays is not printed in the summary file."]),
]
for uc, proto, rel, metric, group, gtitle, stratum, order, endpoint, rationale, srcs, locator, extra in J:
    jid = f"use-case-mapping-{P}-{uc.replace('use-case-', '')}-{proto.split('-protocol-')[-1] if '-protocol-' in proto else proto}"
    jid = jid[:200]
    add({
        "id": jid, "kind": "claim", "name": f"Relevance of {proto} to {uc}",
        "description": "Relevance judgement drafted by the extraction agent; not reviewed.", "status": "needs_review", "facets": {},
        "source_ids": srcs, "links": [{"relation": "subject", "target_id": uc}],
        "attributes": {
            "field": f"links:assessed_by:{proto}", "value": proto, "relevance": rel, "endpoint": endpoint, "rationale": rationale,
            "constraints": ["Inspect every linked evaluation's source locator before citing a result.",
                            "Do not combine this mapping's evaluations with any other protocol's results.",
                            "Compare rows only within this protocol."],
            "limitations": extra + COMMON_LIMITS,
            "citation_locators": [{"source_id": srcs[0], "locator": locator}],
            "source_locator": f"{srcs[0]}: {locator}",
            "headline_metric": metric, "comparison_group": group, "comparison_title": gtitle,
            "stratum_label": stratum, "stratum_order": order,
            "reason": "VEP literature pass 2026-10-14: relevance of a newly extracted protocol (rewire-benchmark-data issues #153-#155).",
            "review": {"method": ["scope-review"], "method_note": "Judgement drafted against the use case's question, inputs and exclusions in data/entities/use-cases.jsonl.",
                       "reviewer": ["claude"], "reviewer_note": COLLECTOR_NOTE, "date": DATE,
                       "note": f"Draft; {len(evals_on(proto))} evaluations on this protocol in this batch. Not reviewed."},
        },
    })

# ---------------------------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------------------------
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids)), "duplicate IDs"
for r in records:
    assert re.fullmatch(r"[a-z0-9][a-z0-9-]{0,254}", r["id"]), r["id"]
for r in records:
    # The store's attribute normaliser keeps missing_metadata keys sorted.
    if "missing_metadata" in r["attributes"]:
        r["attributes"]["missing_metadata"] = dict(sorted(r["attributes"]["missing_metadata"].items()))
records.sort(key=lambda r: r["id"])
with open(os.path.join(out, "batch.jsonl"), "w") as fh:
    for r in records:
        fh.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort()
with open(os.path.join(out, "claims.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
counts = {}
for r in records:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
print(json.dumps(counts, sort_keys=True))
