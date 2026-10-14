"""Extract Brixi et al. 2026 (Nature 652, Evo 2) Supplementary Data 1 into needs_review batch records.

Usage: python3 -I extract_evo2_brixi2026.py <pmc.xml> <MOESM1_ESM.pdf> <MOESM3_ESM.xlsx> <batch folder>

Supplementary Data 1 ('Human variant effect prediction results') is one sheet, 'Sheet1', A1:J706: one row per model
and variant stratum with N_pos, N_neg, N_variants_total, AUROC and AUPRC. Every data row is read with a stdlib OOXML
reader; the header and the row count are asserted. printed_value is the shortest round-trip decimal of the stored
cell value; the cells carry the workbook number format "0.000", recorded as workbook_number_format.
The script asserts the SHA-256 of all three input files before reading.
"""
import csv, hashlib, json, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ooxml import read_sheets

XML, SI, XLSX, OUT = sys.argv[1:5]
XML_SHA = "d043dbda49e023ef6b70e36e7ca7832bda6b7af6c5934368e8778a7f23cda8bd"
SI_SHA = "fe2a99108a4ce5c0f4ef1595605eaec709fa86204410d5b66c1384327eb7b925"
XLSX_SHA = "159f321775d634d9ed53b7a81c5cc1b5ef3d407880997e0f8c69bb8315a20a51"
ESM = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-026-10176-5/MediaObjects/41586_2026_10176_"
SI_URL, XLSX_URL = ESM + "MOESM1_ESM.pdf", ESM + "MOESM3_ESM.xlsx"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13128491/fullTextXML"


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


assert sha256(XML) == XML_SHA and sha256(SI) == SI_SHA and sha256(XLSX) == XLSX_SHA

TODAY = "2026-10-14"
P = "gfm-guides-20261014-evo2-brixi2026"
EXTRACTOR_NOTE = ("Collector agent for issue rewire-bio/rewire-benchmark-data#129 (gfm-guides, 2026-10-14); extraction only, "
                  "not a review. Pending an independent review-evidence pass.")
AREAS, CONTEXTS = ["dna-genomes"], ["research"]
SRC_MAIN = "evidence-official-8717ffb993cc8f7eddec"  # existing record, same artifact (hash matched on re-download)
SRC_SI, SRC_SD1 = P + "-source-supplementary-information", P + "-source-supplementary-data-1"
SRCS = [SRC_MAIN, SRC_SI, SRC_SD1]
DOI = "10.1038/s41586-026-10176-5"


def slug(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", s.lower()) if not unicodedata.combining(c))
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s).strip("-"))


def shortest(raw):
    if re.fullmatch(r"-?\d+", raw):
        return raw
    r = repr(float(raw))
    assert "e" not in r.lower(), raw
    return r


records, ids, claim_rows = [], set(), []


def add(rec):
    assert rec["id"] not in ids, rec["id"]
    ids.add(rec["id"])
    mm = rec["attributes"].get("missing_metadata")
    if mm:
        rec["attributes"]["missing_metadata"] = dict(sorted(mm.items()))
    records.append(rec)
    return rec["id"]


def facets(method_types=None):
    f = {"areas": AREAS, "contexts": CONTEXTS}
    if method_types:
        f["method_types"] = method_types
    return f


def entity(kind, id, name, desc, attrs, source_ids=SRCS, links=(), method_types=None):
    return add({"id": id, "kind": kind, "name": name, "description": desc, "status": "needs_review", "facets": facets(method_types),
                "source_ids": list(source_ids), "links": list(links), "attributes": attrs})


# Sources ---------------------------------------------------------------------------------------------------------
SD1_LIMITS = [
    "Variant counts in Supplementary Data 1 differ from the counts in the Fig. 3 legend: ClinVar coding SNVs 14,313 (legend 14,319), "
    "noncoding SNVs 33,747 (legend 34,761), coding non-SNVs 978 (legend 1,236), noncoding non-SNVs 3,623 (legend 3,894); SpliceVarDB "
    "exonic 1,179 (legend 1,181) and intronic 3,708 (legend 3,769); BRCA1 coding SNVs 2,768 (legend 2,077). BRCA1 noncoding (1,125) and "
    "BRCA1 all SNVs (3,893) match the legend and Supplementary Information A.3.15.",
    "The ClinVar rows with Genomic_Feature 'Both' (SNV 89,126; Indel 25,501; Microsatellite 618 variants) are larger than the sum of the "
    "coding and noncoding rows (SNV 48,060), so 'Both' is not the union of the coding and noncoding strata; the source does not explain the difference.",
    "Coding Indel (1,150) plus coding Microsatellite (172) rows do not sum to the coding non-SNV row (978); the relation between the "
    "'non-SNV', 'Indel' and 'Microsatellite' strata is not stated.",
    "Sub_category labels 'Poorly conserved' and 'Not conserved' do not match the bin names in Supplementary Information A.3.13 "
    "('weakly conserved', 0 <= phyloP < 0.5; 'accelerated evolution', phyloP < 0); the mapping is not stated.",
    "Model label spelling differs within the sheet: 'phyloP 100/241/447/470' on SpliceVarDB rows and 'PhyloP 100/241/447/470' elsewhere.",
    "AUROC and AUPRC cells store full-precision doubles and carry the number format '0.000', so the workbook displays three decimals.",
    "No uncertainty (confidence interval or standard error) is given for any value.",
]
entity("source", SRC_SI, "Genome modelling and design across all domains of life with Evo 2: Supplementary Information (Nature 2026)",
       "Primary source retrieved and hashed for the issue #129 Evo 2 evidence pass.", {
           "url": "https://doi.org/" + DOI, "artifact_url": SI_URL,
           "version": "Nature 652 (2026), published 2026-03-04; Supplementary Information file 41586_2026_10176_MOESM1_ESM.pdf (73 pages)",
           "retrieved_at": "2026-10-14T12:01:04Z", "artifact_sha256": SI_SHA, "doi": DOI, "publication_status": "peer_reviewed",
           "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf",
           "limitations": [
               "Supplementary Tables 6 to 8 print Evo 2 7B base zero-shot AUROC and AUPRC against a 7B data-ablation model on ClinVar, "
               "SpliceVarDB and BRCA1. Several Evo 2 7B base values differ from Supplementary Data 1: ClinVar all SNV AUROC 0.957 and AUPRC "
               "0.927 (Supplementary Data 1 'Both' SNV 0.960 and 0.944), coding non-SNV AUROC 0.918 (0.865), SpliceVarDB intronic AUROC 0.923 "
               "(0.925). BRCA1 values match. The tables were not extracted.",
               "Licence CC BY-NC-ND 4.0 (article licence statement); no archived copy kept in the batch folder.",
           ],
       }, source_ids=[])
entity("source", SRC_SD1, "Genome modelling and design across all domains of life with Evo 2: Supplementary Data 1, human variant effect prediction results (Nature 2026)",
       "Primary source retrieved and hashed for the issue #129 Evo 2 evidence pass.", {
           "url": "https://doi.org/" + DOI, "artifact_url": XLSX_URL,
           "version": "Nature 652 (2026), published 2026-03-04; Supplementary Data 1 file 41586_2026_10176_MOESM3_ESM.xlsx",
           "retrieved_at": "2026-10-14T12:01:04Z", "artifact_sha256": XLSX_SHA, "doi": DOI, "publication_status": "peer_reviewed",
           "licence": "CC-BY-NC-ND-4.0", "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
           "source_locator": "Sheet 'Sheet1', A1:J706",
           "limitations": SD1_LIMITS + ["Licence CC BY-NC-ND 4.0 (article licence statement); no archived copy kept in the batch folder."],
       }, source_ids=[])

# Read the sheet --------------------------------------------------------------------------------------------------
sheet = read_sheets(XLSX)["Sheet1"]
HEAD = ["Model", "Data", "Genomic_Feature", "Variant_Type", "Sub_category", "N_pos", "N_neg", "N_variants_total", "AUROC", "AUPRC"]
assert [sheet[c + "1"][0] for c in "ABCDEFGHIJ"] == HEAD
rows = []
for r in range(2, 707):
    cell = lambda c: sheet.get(f"{c}{r}", (None, None, None))
    vals = {h: cell(c)[0] for h, c in zip(HEAD, "ABCDEFGHIJ")}
    assert all(cell(c)[1] is None for c in "ABCDEFGHIJ"), r  # no formulas
    assert vals["Model"] and vals["AUROC"] is not None and vals["AUPRC"] is not None, r
    rows.append((r, vals))
assert not any(int(re.sub(r"\D", "", k)) > 706 for k in sheet), "rows beyond 706"
assert len(rows) == 705

# Benchmark, datasets, protocols ---------------------------------------------------------------------------------
BENCH = P + "-benchmark-human-vep"
entity("benchmark", BENCH, "Evo 2 paper zero-shot human variant effect evaluations (Brixi et al. 2026)",
       "Zero-shot classification of human variants from ClinVar, SpliceVarDB and BRCA1/BRCA2 functional assays, scored with Evo 2 and "
       "comparison models by the Evo 2 authors; AUROC and AUPRC per variant stratum in Supplementary Data 1.", {
           "entity_level": "suite", "version": "As published, Nature 652 (2026)",
           "task": "Classify pathogenic or loss-of-function human variants from benign or functional variants by zero-shot model scores",
           "scope_note": "Protocols are the variant strata of Supplementary Data 1; one evaluation per model and stratum.",
           "source_locator": "Main text 'Human variant effect prediction' and Fig. 3 legend; Supplementary Information A.3.12 to A.3.15; Supplementary Data 1",
       })

DATA = {
    "ClinVar": (P + "-data-clinvar-2024-10", "ClinVar October 2024 release, filtered (Brixi et al. 2026)",
                "ClinVar variants used by the Evo 2 authors: nuclear genome, review status of at least two stars, at most 64 bp of reference or "
                "alternate allele, variants of unknown significance removed, loci with matched transcript IDs in the GRCh38.p14 GTF.",
                {"version": "ClinVar October 2024 release", "split": "No split; all filtered variants scored zero-shot",
                 "label_semantics": "Pathogenic/Likely pathogenic versus Benign/Likely benign",
                 "source_locator": "Supplementary Information A.3.13 (page 13)"}),
    "SpliceVarDB": (P + "-data-splicevardb", "SpliceVarDB experimentally validated splice variants (Brixi et al. 2026)",
                    "SpliceVarDB variants with experimentally validated splicing effects, excluding variants labelled 'low frequency'.",
                    {"split": "No split; all retained variants scored zero-shot",
                     "label_semantics": "Variants that cause aberrant splicing versus other variants (SpliceVarDB classification; class names not printed)",
                     "source_locator": "Supplementary Information A.3.14 (page 14); Fig. 3d legend",
                     "missing_metadata": {"version": {"reason": "unreported", "note": "SpliceVarDB release or download date not stated"}}}),
    "BRCA1": (P + "-data-brca1-sge-findlay2018", "BRCA1 saturation genome editing SNVs, Findlay et al. 2018 classes (Brixi et al. 2026)",
              "BRCA1 SNVs with functional scores and classes from saturation genome editing (Findlay et al. 2018, reference 26): LOF (823) "
              "versus FUNC (2,821) plus INT (249), 3,893 SNVs in coding and noncoding regions.",
              {"version": "Findlay et al. 2018 (Nature 562, 217-222) classifications", "positives": 823, "negatives": 3070,
               "split": "No split for zero-shot scoring",
               "label_semantics": "LOF versus FUNC and INT combined",
               "source_locator": "Supplementary Information A.3.15 (page 14); Fig. 3e legend"}),
    "BRCA2": (P + "-data-brca2-huang2025", "BRCA2 SNVs with functional classifications, Huang et al. 2025 (Brixi et al. 2026)",
              "BRCA2 SNVs with experimental functional scores and classifications (Huang et al. 2025, reference 27): P strong, P moderate "
              "and P supporting (1,156) versus B strong, B moderate and B supporting (5,681).",
              {"version": "Huang et al. 2025 (Nature 638, 528-537) classifications", "positives": 1156, "negatives": 5681,
               "split": "No split for zero-shot scoring",
               "label_semantics": "P strong, P moderate, P supporting versus B strong, B moderate, B supporting",
               "source_locator": "Supplementary Information A.3.15 (page 14); main text 'Human variant effect prediction'"}),
}
for key, (did, name, desc, attrs) in DATA.items():
    entity("dataset", did, name, desc, attrs)

FEATURE = {"Coding": "coding", "Noncoding": "noncoding", "Both": "'Both' (coding and noncoding)", "Exonic": "exonic",
           "Intronic": "intronic", "Splice region": "splice region",
           "Low SpliceAI/Pangolin scores": "low SpliceAI and Pangolin scores (both below 0.1)"}
VTYPE = {"SNV": "SNVs", "non-SNV": "non-SNVs", "Non-SNV": "non-SNVs", "Indel": "indels", "Microsatellite": "microsatellite variants"}
SUB_NOTE = {
    "Far from splice site": "Label 'Far from splice site'; SI A.3.13 defines only 'Near to splice site'.",
    "Near splice site": "Within 3 bp of the nearest splice donor or 5 bp of the nearest splice acceptor (SI A.3.13).",
    "Highly conserved": "phyloP 100-way > 2 (SI A.3.13).",
    "Moderately conserved": "0.5 <= phyloP 100-way <= 2 (SI A.3.13).",
    "Poorly conserved": "Label 'Poorly conserved'; SI A.3.13 names its bins 'weakly conserved' (0 <= phyloP < 0.5) and 'accelerated evolution' (phyloP < 0); the mapping is not stated.",
    "Not conserved": "Label 'Not conserved'; SI A.3.13 names its bins 'weakly conserved' (0 <= phyloP < 0.5) and 'accelerated evolution' (phyloP < 0); the mapping is not stated.",
    "Intergenic": "Label 'Intergenic'; no further definition in the SI.",
}
POS = {"ClinVar": "pathogenic/likely pathogenic", "SpliceVarDB": "splice-altering", "BRCA1": "loss-of-function (LOF)",
       "BRCA2": "loss-of-function (P classes)"}
NEG = {"ClinVar": "benign/likely benign", "SpliceVarDB": "other", "BRCA1": "functional or intermediate (FUNC, INT)",
       "BRCA2": "functional (B classes)"}
PROTO_SI = {"ClinVar": "SI A.3.12 and A.3.13 (page 13)", "SpliceVarDB": "SI A.3.12 and A.3.14 (pages 13 and 14)",
            "BRCA1": "SI A.3.12 and A.3.15 (pages 13 and 14)", "BRCA2": "SI A.3.12 and A.3.15 (pages 13 and 14)"}
FIG = {("ClinVar", "Coding"): "Fig. 3b", ("ClinVar", "Noncoding"): "Fig. 3c", ("SpliceVarDB", "Exonic"): "Fig. 3d",
       ("SpliceVarDB", "Intronic"): "Fig. 3d", ("BRCA1", "Coding"): "Fig. 3e", ("BRCA1", "Noncoding"): "Fig. 3e",
       ("BRCA1", "Both"): "Extended Data Fig. 5a", ("BRCA1", "Intronic"): "Extended Data Fig. 5b",
       ("BRCA1", "Splice region"): "Extended Data Fig. 5b", ("BRCA2", "Both"): "Extended Data Fig. 5c"}

strata = {}
for r, v in rows:
    k = (v["Data"], v["Genomic_Feature"], v["Variant_Type"], v["Sub_category"])
    counts = (v["N_pos"], v["N_neg"], v["N_variants_total"])
    assert int(counts[0]) + int(counts[1]) == int(counts[2]), r
    if k in strata:
        assert strata[k] == counts, (r, k)  # same variants for every model in a stratum
    strata[k] = counts
assert len(strata) == 49
# positive-class mapping checked against SI A.3.15 counts
assert strata[("BRCA1", "Both", "SNV", None)][:2] == ("823", "3070")
assert strata[("BRCA2", "Both", "SNV", None)][:2] == ("1156", "5681")


def stratum_label(k):
    d, f, t, s = k
    lab = f"{d} {FEATURE[f]} {VTYPE[t]}"
    return lab + (f", {s[0].lower() + s[1:]}" if s else "")


PROT = {}
for k, (npos, nneg, ntot) in strata.items():
    d, f, t, s = k
    pid = P + "-protocol-" + slug("-".join(x for x in (d, f, t, s) if x))
    PROT[k] = pid
    lab = stratum_label(k)
    fig = FIG.get((d, f)) if s is None else "Extended Data Fig. 4"
    limits = [f"Positives: {npos} {POS[d]}; negatives: {nneg} {NEG[d]}; total {ntot} variants (Supplementary Data 1).",
              "No split: every model scores the same variants zero-shot (SI A.3.12: 'For each benchmark, we score the same variants with all models').",
              "Supervised comparators (AlphaMissense, CADD, SpliceAI, Pangolin) may have been trained on overlapping variants; training overlap is not reported.",
              "No uncertainty is reported."]
    if s:
        limits.insert(1, SUB_NOTE[s])
    if f == "Both" and d == "ClinVar":
        limits.insert(1, "The 'Both' rows are larger than the sum of the coding and noncoding rows; the population is not explained in the source.")
    entity("protocol", pid, f"Zero-shot {lab} classification (Evo 2 paper, Supplementary Data 1)",
           f"Zero-shot classification of {POS[d]} versus {NEG[d]} variants in the {lab} stratum, AUROC and AUPRC.", {
               "protocol": (f"Score each variant zero-shot (for Evo 2, the log-likelihood of the variant sequence minus that of the reference over an "
                            f"8,192-bp genomic window around the variant) and compute AUROC and AUPRC for {POS[d]} versus {NEG[d]} variants in the stratum "
                            f"Data '{d}', Genomic_Feature '{f}', Variant_Type '{t}'" + (f", Sub_category '{s}'" if s else "") + "."),
               "version": "As published, Nature 652 (2026), Supplementary Data 1",
               "source_locator": f"Supplementary Data 1 rows with Data '{d}', Genomic_Feature '{f}', Variant_Type '{t}', Sub_category '{s or ''}'; {PROTO_SI[d]}"
                                 + (f"; {fig}" if fig else ""),
               "limitations": limits,
           }, links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": DATA[d][0]}])

# Models and configurations ---------------------------------------------------------------------------------------
NEW_MODELS = {
    "codonbert": ("CodonBERT", "BERT-style language model of mRNA coding sequences at codon resolution.", "Reference 124 in the SI (Li et al.); SI A.3.11 ('BERT-style model focused on codon usage')"),
    "encodon": ("EnCodon", "Encoder-only codon language model.", "Reference 125 in the SI (Naghipourfar et al., bioRxiv 2024); SI A.3.11 ('encoder-only architecture')"),
    "decodon": ("DeCodon", "Decoder-only codon language model.", "Reference 125 in the SI (Naghipourfar et al., bioRxiv 2024); SI A.3.11 ('decoder-only architecture')"),
}
FAMILY = {"evo2": "discovery-model-evo-2", "evo1": "lit-genomics-20261011-geneb-model-evo",
          "alphamissense": "somatic-oncogenicity-20261009-method-alphamissense", "cadd": "somatic-oncogenicity-20261009-method-cadd",
          "esm1b": "uc20260930-model-esm-1b", "esm2": "discovery-model-esm-2", "gpnmsa": "regulatory-variant-20261009-model-gpn",
          "nt": "discovery-model-nucleotide-transformer", "pangolin": "discovery-model-pangolin", "phylop": "somatic-oncogenicity-20261009-method-phylop",
          "rnafm": "discovery-model-rna-fm", "spliceai": "discovery-model-spliceai"}
for key, (name, desc, loc) in NEW_MODELS.items():
    FAMILY[key] = entity("model", P + "-model-" + key, name, desc, {
        "entity_level": "family", "reported_name": name, "source_locator": loc,
        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the checkpoint is on the configuration"}},
    }, source_ids=[SRC_SI], method_types=["foundation_model"])

FM, SUP, CONS = ["foundation_model"], ["supervised_machine_learning"], ["conventional_pipeline"]
EVO2_IN = "8,192-bp genomic window around the variant; variant log-likelihood minus reference log-likelihood (SI A.3.12)"
DNA_IN = "DNA sequence around the variant (window not stated); change in likelihood or masked marginal likelihood (SI A.3.12)"
PROT_IN = "Amino-acid sequence of the gene; masked marginal likelihood for SNVs, change in pseudolikelihood for non-SNVs (SI A.3.12)"
PHYLOP_IN = "PhyloP score at the variant; mean over affected reference positions for non-SNVs (SI A.3.12)"
# label: (key, family, version or None, parameters, method types, foundation_model_eligible, inputs, adaptation, access, locator)
CONFIGS = {
    "Evo 2 40B": ("evo-2-40b", "evo2", "Evo 2 40B, 1M-token context after midtraining", "40B parameters; context extended to 1,048,576 tokens (SI Supplementary Table 3)", FM, True, EVO2_IN, "zero-shot",
                  "Released openly with training and inference code, data and parameters (Discussion)", "SI A.1.4 and Supplementary Table 3 (page 3); Discussion"),
    "Evo 2 7B": ("evo-2-7b", "evo2", "Evo 2 7B, 1M-token context after midtraining", "7B parameters; context extended to 1,048,576 tokens (SI Supplementary Table 3)", FM, True, EVO2_IN, "zero-shot",
                 "Released openly with training and inference code, data and parameters (Discussion)", "SI A.1.4 and Supplementary Table 3 (page 3); Discussion"),
    "Evo 2 40B base": ("evo-2-40b-base", "evo2", "Evo 2 40B base: after pretraining, before context extension", "40B parameters; pretraining sequence length 1,024 then 8,192 (SI Supplementary Table 2)", FM, True, EVO2_IN, "zero-shot",
                       None, "SI A.1.4 and Supplementary Table 2 (page 3)"),
    "Evo 2 7B base": ("evo-2-7b-base", "evo2", "Evo 2 7B base: after pretraining, before context extension", "7B parameters; pretraining sequence length 8,192 (SI Supplementary Table 2)", FM, True, EVO2_IN, "zero-shot",
                      None, "SI A.1.4 and Supplementary Table 2 (page 3)"),
    "Evo 1": ("evo-1", "evo1", None, "Predecessor Evo model; checkpoint for variant scoring not stated", FM, True, DNA_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
    "NT": ("nt", "nt", None, "Nucleotide Transformer (reference 105); checkpoint for variant scoring not stated", FM, True, DNA_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
    "ESM-1b": ("esm-1b", "esm1b", "ESM-1b", "Protein language model (reference 127)", FM, True, PROT_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
    "ESM-2 650M": ("esm-2-650m", "esm2", "ESM-2 650M", "Protein language model, 650M parameters (reference 109)", FM, True, PROT_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
    "CodonBERT 87M": ("codonbert-87m", "codonbert", "CodonBERT 87M", "Codon language model, 87M parameters as labelled (reference 124)", FM, True, None, "zero-shot", None, "SI A.3.12 (page 13)"),
    "EnCodon 620M": ("encodon-620m", "encodon", "EnCodon 620M", "Encoder-only codon language model, 620M parameters as labelled (reference 125)", FM, True, None, "zero-shot", None, "SI A.3.12 (page 13)"),
    "DeCodon 200M": ("decodon-200m", "decodon", "DeCodon 200M", "Decoder-only codon language model, 200M parameters as labelled (reference 125)", FM, True, None, "zero-shot", None, "SI A.3.12 (page 13)"),
    "RNA-FM": ("rna-fm", "rnafm", None, "RNA language model (reference 128); checkpoint not stated", FM, True, None, "zero-shot", None, "SI A.3.12 (page 13)"),
    "GPN-MSA": ("gpn-msa", "gpnmsa", None, "Alignment-based DNA language model (reference 92); scores SNVs only", FM, True, None, "zero-shot", None, "SI A.3.12 (page 13)"),
    "AlphaMissense": ("alphamissense", "alphamissense", None, "Missense variant effect predictor (reference 129); scores SNVs at fixed coordinates only", SUP, False, None, None, None, "SI A.3.12 (page 13)"),
    "CADD": ("cadd", "cadd", None, "Variant effect ensemble (reference 132 is the CADD v1.7 paper; the version used is not stated)", SUP, False, None, None, None, "SI A.3.12 (page 13)"),
    "SpliceAI": ("spliceai", "spliceai", None, "Supervised splicing predictor (reference 130)", SUP, False, None, None, None, "SI A.3.12 (page 13)"),
    "Pangolin": ("pangolin", "pangolin", None, "Supervised splicing predictor (reference 131); score is the maximum absolute predicted change in splice site usage", SUP, False,
                 "Maximum absolute predicted increase or decrease in splice site usage around the variant (SI A.3.12)", None, None, "SI A.3.12 (page 13)"),
    "PhyloP 100": ("phylop-100", "phylop", "PhyloP100", "Conservation score from a 100-way alignment", CONS, False, PHYLOP_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
    "PhyloP 241": ("phylop-241", "phylop", "PhyloP241", "Conservation score from a 241-way alignment", CONS, False, PHYLOP_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
    "PhyloP 447": ("phylop-447", "phylop", "PhyloP447", "Conservation score from a 447-way alignment", CONS, False, PHYLOP_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
    "PhyloP 470": ("phylop-470", "phylop", "PhyloP470", "Conservation score from a 470-way alignment", CONS, False, PHYLOP_IN, "zero-shot", None, "SI A.3.12 (page 13)"),
}
LABEL_ALIAS = {"phyloP 100": "PhyloP 100", "phyloP 241": "PhyloP 241", "phyloP 447": "PhyloP 447", "phyloP 470": "PhyloP 470"}
assert {LABEL_ALIAS.get(v["Model"], v["Model"]) for _, v in rows} == set(CONFIGS)

CFG = {}
for label, (key, fam, version, params, mtypes, fme, _inp, _adapt, access, loc) in CONFIGS.items():
    spellings = [label] + [a for a, b in LABEL_ALIAS.items() if b == label]
    attrs = {"reported_name": label, "foundation_model_eligible": fme, "parameters": params,
             "source_locator": f"Supplementary Data 1 column 'Model' ({', '.join(repr(s) for s in spellings)}); {loc}"}
    miss = {}
    if version:
        attrs["version"] = version
    else:
        miss["version"] = {"reason": "unreported", "note": "Checkpoint or release used for variant scoring not stated"}
    if access:
        attrs["access_reuse"] = access
    else:
        miss["access_reuse"] = {"reason": "unextracted"}
    miss["checkpoint_revision"] = {"reason": "unreported"}
    attrs["missing_metadata"] = miss
    CFG[label] = entity("configuration", P + "-config-" + key, f"{label} (Evo 2 paper variant effect evaluations)",
                        f"{label} as scored zero-shot by the Evo 2 authors on human variant effect benchmarks.", attrs,
                        links=[{"relation": "configuration_of", "target_id": FAMILY[fam]}], method_types=mtypes)

# Evaluations and results -----------------------------------------------------------------------------------------
METHOD_NOTE = ("Read sheet 'Sheet1' of the pinned Supplementary Data 1 workbook with a stdlib OOXML reader (extract/ooxml.py); header "
               "A1:J1 and 705 data rows asserted; printed_value is the shortest round-trip decimal of the stored cell value; the "
               "cell number format is '0.000'.")
DVER = {"ClinVar": "ClinVar October 2024 release, filtered as in SI A.3.13", "SpliceVarDB": None,
        "BRCA1": "Findlay et al. 2018 SGE classes", "BRCA2": "Huang et al. 2025 classes"}
seen = set()
for r, v in rows:
    label = LABEL_ALIAS.get(v["Model"], v["Model"])
    k = (v["Data"], v["Genomic_Feature"], v["Variant_Type"], v["Sub_category"])
    assert (label, k) not in seen, (r, label, k)
    seen.add((label, k))
    key, fam, version, params, mtypes, fme, inputs, adapt, access, loc = CONFIGS[label]
    pid = PROT[k]
    lab = stratum_label(k)
    suffix = pid[len(P + "-protocol-"):]
    ev = P + "-eval-" + key + "-" + suffix
    sel = f"row {r}: Model '{v['Model']}', Data '{k[0]}', Genomic_Feature '{k[1]}', Variant_Type '{k[2]}', Sub_category '{k[3] or ''}'"
    comparison = {"protocol_id": pid, "dataset_version": DVER[k[0]], "split": "No split; all variants in the stratum scored",
                  "population": f"{lab}: {v['N_pos']} {POS[k[0]]}, {v['N_neg']} {NEG[k[0]]}, {v['N_variants_total']} total",
                  "inputs": inputs, "adaptation": adapt, "metric_implementation": None, "aggregation": None, "budget": None}
    miss = {"comparison." + f: {"reason": "unreported"} for f, x in comparison.items() if x is None}
    if adapt is None:
        miss["comparison.adaptation"] = {"reason": "unreported", "note": "Described as a supervised predictor; whether precomputed scores or a re-run model was used is not stated"}
    add({"id": ev, "kind": "evaluation", "name": f"{label} on {lab} (Evo 2 paper)",
         "description": "Published comparison transcribed from the pinned source; not reproduced.", "status": "needs_review",
         "facets": facets(), "source_ids": SRCS,
         "links": [{"relation": "system", "target_id": CFG[label]}, {"relation": "assessment", "target_id": pid},
                   {"relation": "data", "target_id": DATA[k[0]][0]}],
         "attributes": {"origin": "author_reported", "protocol": pid, "version": "Primary source as retrieved " + TODAY,
                        "comparison": comparison, "source_locator": f"Supplementary Data 1 (sheet 'Sheet1') {sel}",
                        "missing_metadata": miss}})
    for col, metric, head in (("I", "auroc", "AUROC"), ("J", "auprc", "AUPRC")):
        raw = sheet[f"{col}{r}"][0]
        printed = shortest(raw)
        locator = f"Supplementary Data 1 (sheet 'Sheet1') cell {col}{r}, {sel}, column '{head}'"
        rid = P + "-result-" + key + "-" + suffix + "-" + metric
        add({"id": rid, "kind": "result", "name": f"{label} {head}, {lab} (Evo 2 paper Supplementary Data 1)",
             "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.", "status": "needs_review",
             "facets": {}, "source_ids": [SRC_SD1, SRC_SI], "links": [{"relation": "evaluation", "target_id": ev}],
             "attributes": {"metric": metric, "metric_direction": "higher", "unit": "unitless", "printed_value": printed,
                            "numeric_value": printed, "metric_qualifier": f"zero-shot; {lab}", "source_locator": locator,
                            "raw_xml_value": raw, "workbook_number_format": "0.000",
                            "review": {"method": ["deterministic-table-parse"], "method_note": METHOD_NOTE, "reviewer": ["claude"],
                                       "reviewer_note": EXTRACTOR_NOTE, "date": TODAY, "artifact_sha256": XLSX_SHA, "retrieval_url": XLSX_URL,
                                       "note": "Extracted, not reviewed. The review-evidence pass must re-check this cell against the pinned artifact."},
                            "missing_metadata": {"uncertainty": {"reason": "unreported"}}}})
        claim_rows.append([rid, SRC_SD1, locator, printed, "result"])
assert len(seen) == 705

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for rec in sorted(records, key=lambda x: x["id"]):
        f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(OUT, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for row in sorted(claim_rows):
        w.writerow(row)
counts = {}
for rec in records:
    counts[rec["kind"]] = counts.get(rec["kind"], 0) + 1
print(json.dumps(dict(sorted(counts.items()))))
