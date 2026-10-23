"""Extract Lu, Liu, Lin and Brandes, 'Genomic heterogeneity inflates the performance of variant pathogenicity
predictions' (bioRxiv 10.1101/2025.09.05.674459 v2) into a needs_review batch.

Usage:
  python3 -I extract/build_batch.py <artifact-dir> <batch-folder>

<artifact-dir> holds the pinned PDF as lu-brandes-v2.full.pdf. Its hash is asserted before anything is read.

Figure 1 and Supplementary Figure S2 print a numeric label beside every bar, with the method named on the
y axis and the variant group, N and %P in each panel title. The figures are drawn without a text layer, so
their labels were transcribed by the extractor from 400 dpi renders of page 8 and a 200 dpi render of page 21
(pdftoppm, poppler 26.08.0) into FIG1 and FIGS2 below. Every value the text also prints is asserted equal to
the transcription, and the text sentences are asserted as exact substrings of the pdftotext -layout text.
All records are written with status needs_review.
"""
import csv, hashlib, json, os, re, subprocess, sys

TODAY = "2026-10-19"
P = "lu-hetero-20261019"
PDF = "lu-brandes-v2.full.pdf"
PDF_SHA = "5b8e939257000811a6eaddd90d9de3e03bf1ac0e9015a38769df887ee01f9bf2"
PDF_URL = "https://www.biorxiv.org/content/10.1101/2025.09.05.674459v2.full.pdf"
RETRIEVED = "2026-10-19T12:23:08Z"
EXTRACTOR_NOTE = ("Extractor: Claude (Opus 5.5) automated research agent; extraction only, not independent review; "
                  "no human review claimed.")
AREAS = ["dna-genomes"]
S = P + "-source-preprint-v2"

# Existing records reused (never changed).
MODELS = {
    "AlphaGenome": "catalog-model-alphagenome",
    "Evo2": "discovery-model-evo-2",
    "GPN-MSA": "gfm-guides-20261014-gpnmsa-model-gpn-msa",
    "PhyloGPN": "lit-genomics-20261011-guanine-model-phylogpn",
    "Nucleotide Transformer": "discovery-model-nucleotide-transformer",
    "DNABERT2": "catalog-model-dnabert-2",
    "ESM1b": "uc20260930-model-esm-1b",
    "ESM1v": "discovery-model-esm-1v",
    "ESM2": "catalog-model-esm-2",
    "AlphaMissense": "somatic-oncogenicity-20261009-method-alphamissense",
    "PrimateAI-3D": "vep-uc-20261014-method-primateai-3d",
    "PhyloP": "somatic-oncogenicity-20261009-method-phylop",
}

# Figure 1 (page 8). Panel key -> (printed title, N, %P, [(row label, printed AUROC), ...]) in printed order.
FIG1 = {
    "all-variants": ("All variants", "258,944", "30.59%", [("Evo2", "0.969"), ("Rule-based", "0.962"), ("GPN-MSA", "0.960"), ("PhyloGPN", "0.915"), ("PhyloP", "0.908"), ("Nucleotide Transformer", "0.793"), ("DNABERT2", "0.576"), ("AlphaGenome", "0.310")]),
    "noncoding": ("Noncoding", "118,256", "10.69%", [("AlphaGenome", "0.991"), ("GPN-MSA", "0.981"), ("PhyloP", "0.976"), ("Evo2", "0.975"), ("PhyloGPN", "0.951"), ("Rule-based", "0.944"), ("Nucleotide Transformer", "0.851"), ("DNABERT2", "0.433")]),
    "intron-non-splice": ("Intron (Non-splice)", "88,049", "1.60%", [("AlphaGenome", "0.960"), ("Evo2", "0.903"), ("GPN-MSA", "0.885"), ("PhyloP", "0.852"), ("PhyloGPN", "0.846"), ("Nucleotide Transformer", "0.750"), ("DNABERT2", "0.437")]),
    "splice": ("Splice", "11,042", "99.30%", [("GPN-MSA", "0.775"), ("PhyloP", "0.727"), ("PhyloGPN", "0.722"), ("Evo2", "0.697"), ("Nucleotide Transformer", "0.617"), ("AlphaGenome", "0.592"), ("DNABERT2", "0.454")]),
    "utr3": ("3' UTR", "11,851", "0.21%", [("GPN-MSA", "0.908"), ("PhyloP", "0.862"), ("AlphaGenome", "0.789"), ("PhyloGPN", "0.765"), ("Evo2", "0.747"), ("Nucleotide Transformer", "0.564"), ("DNABERT2", "0.499")]),
    "utr5": ("5' UTR", "2,471", "2.38%", [("Evo2", "0.767"), ("GPN-MSA", "0.728"), ("PhyloP", "0.696"), ("PhyloGPN", "0.601"), ("AlphaGenome", "0.580"), ("Nucleotide Transformer", "0.567"), ("DNABERT2", "0.414")]),
    "rna-gene": ("RNA gene", "131", "25.95%", [("GPN-MSA", "0.938"), ("PhyloP", "0.882"), ("AlphaGenome", "0.851"), ("PhyloGPN", "0.476"), ("Evo2", "0.459"), ("DNABERT2", "0.423"), ("Nucleotide Transformer", "0.371")]),
    "synonymous": ("Synonymous", "42,139", "0.66%", [("AlphaGenome", "0.919"), ("Evo2", "0.885"), ("GPN-MSA", "0.882"), ("PhyloP", "0.855"), ("PhyloGPN", "0.806"), ("Nucleotide Transformer", "0.770"), ("DNABERT2", "0.552")]),
    "stop-loss": ("Stop loss", "94", "75.53%", [("GPN-MSA", "0.888"), ("Evo2", "0.826"), ("PhyloP", "0.796"), ("PhyloGPN", "0.695"), ("Nucleotide Transformer", "0.609"), ("DNABERT2", "0.570"), ("AlphaGenome", "0.362")]),
    "start-loss": ("Start loss", "847", "97.53%", [("GPN-MSA", "0.769"), ("Evo2", "0.711"), ("ESM2", "0.709"), ("ESM1b", "0.681"), ("PhyloP", "0.675"), ("ESM1v", "0.638"), ("PhyloGPN", "0.583"), ("Nucleotide Transformer", "0.569"), ("AlphaGenome", "0.523"), ("DNABERT2", "0.389")]),
    "missense": ("Missense", "50,820", "40.09%", [("AlphaMissense", "0.959"), ("PrimateAI-3D", "0.943"), ("ESM1b", "0.919"), ("GPN-MSA", "0.906"), ("ESM2", "0.886"), ("ESM1v", "0.886"), ("PhyloP", "0.856"), ("Evo2", "0.836"), ("PhyloGPN", "0.799"), ("Nucleotide Transformer", "0.594"), ("AlphaGenome", "0.560"), ("DNABERT2", "0.484")]),
    "missense-and-intron": ("Missense & Intron (Non-splice)", "255", "17.91%", [("AlphaMissense", "0.924"), ("PrimateAI-3D", "0.905"), ("GPN-MSA", "0.896"), ("PhyloP", "0.868"), ("Evo2", "0.835"), ("ESM2", "0.818"), ("ESM1b", "0.800"), ("ESM1v", "0.769"), ("PhyloGPN", "0.689"), ("Nucleotide Transformer", "0.664"), ("AlphaGenome", "0.583"), ("DNABERT2", "0.449")]),
    "missense-and-utr3": ("Missense & 3'UTR", "117", "40.97%", [("AlphaMissense", "0.952"), ("PrimateAI-3D", "0.937"), ("ESM1b", "0.906"), ("Evo2", "0.896"), ("GPN-MSA", "0.887"), ("ESM2", "0.878"), ("ESM1v", "0.870"), ("PhyloP", "0.853"), ("PhyloGPN", "0.729"), ("DNABERT2", "0.546"), ("Nucleotide Transformer", "0.546"), ("AlphaGenome", "0.508")]),
    "stop-gain": ("Stop gain", "42,408", "98.13%", [("AlphaMissense", "0.849"), ("PrimateAI-3D*", "0.817"), ("ESM1b", "0.788"), ("GPN-MSA", "0.783"), ("PhyloP", "0.704"), ("ESM2", "0.684"), ("PhyloGPN", "0.677"), ("Evo2", "0.663"), ("ESM1v", "0.656"), ("Nucleotide Transformer", "0.618"), ("DNABERT2", "0.483"), ("AlphaGenome", "0.389")]),
}
FIG1_COORD = {  # column and position of each panel on page 8, for locators
    "all-variants": "column 1, panel 1", "noncoding": "column 1, panel 2", "intron-non-splice": "column 1, panel 3", "splice": "column 1, panel 4",
    "utr3": "column 1, panel 5", "utr5": "column 2, panel 1", "rna-gene": "column 2, panel 2", "synonymous": "column 2, panel 3",
    "stop-loss": "column 2, panel 4", "start-loss": "column 2, panel 5", "missense": "column 3, panel 1", "missense-and-intron": "column 3, panel 2",
    "missense-and-utr3": "column 3, panel 3", "stop-gain": "column 3, panel 4"}

# Supplementary Figure S2 (page 21): AlphaGenome scorers on splice variants (N=11,047, %P=99.32%).
FIGS2 = [("All outputs (quantile)", "0.614", "all-outputs-quantile"), ("All splice outputs (raw)", "0.708", "splice-outputs-raw"),
         ("All splice outputs (quantile)", "0.614", "splice-outputs-quantile"), ("Splice site usage (raw)", "0.779", "splice-site-usage-raw"),
         ("Splice site usage (quantile)", "0.699", "splice-site-usage-quantile"), ("Splice site (raw)", "0.706", "splice-site-raw"),
         ("Splice site (quantile)", "0.683", "splice-site-quantile"), ("Splice junction (raw)", "0.669", "splice-junction-raw"),
         ("Splice junction (quantile)", "0.600", "splice-junction-quantile")]

# Prose values asserted against the figure transcription: (sentence in the text, panel, row label, value).
PROSE = [
    ("Evo2 appears to perform very well across all noncoding variants (AUROC=0.975)", "noncoding", "Evo2", "0.975"),
    ("(e.g., 0.903 for non-splice intron variants, 0.697 for canonical splice sites)", "intron-non-splice", "Evo2", "0.903"),
    ("(e.g., 0.903 for non-splice intron variants, 0.697 for canonical splice sites)", "splice", "Evo2", "0.697"),
    ("This information alone yields strong separation between clinical labels across all variants (AUROC=0.962) and noncoding variants (AUROC=0.944; Figure 1).", "all-variants", "Rule-based", "0.962"),
    ("This information alone yields strong separation between clinical labels across all variants (AUROC=0.962) and noncoding variants (AUROC=0.944; Figure 1).", "noncoding", "Rule-based", "0.944"),
    ("AlphaGenome performed best (AUROC=0.960), followed by Evo2 (0.903) and GPN-MSA (0.885) that also exceeded PhyloP (0.852).", "intron-non-splice", "AlphaGenome", "0.960"),
    ("AlphaGenome performed best (AUROC=0.960), followed by Evo2 (0.903) and GPN-MSA (0.885) that also exceeded PhyloP (0.852).", "intron-non-splice", "GPN-MSA", "0.885"),
    ("AlphaGenome performed best (AUROC=0.960), followed by Evo2 (0.903) and GPN-MSA (0.885) that also exceeded PhyloP (0.852).", "intron-non-splice", "PhyloP", "0.852"),
    ("with only GPN-MSA (0.775) surpassing PhyloP (0.727), while AlphaGenome dropped to 0.592.", "splice", "GPN-MSA", "0.775"),
    ("with only GPN-MSA (0.775) surpassing PhyloP (0.727), while AlphaGenome dropped to 0.592.", "splice", "PhyloP", "0.727"),
    ("with only GPN-MSA (0.775) surpassing PhyloP (0.727), while AlphaGenome dropped to 0.592.", "splice", "AlphaGenome", "0.592"),
    ("In 3’ UTR variants, only GPN-MSA (0.908) outperformed PhyloP (0.862).", "utr3", "GPN-MSA", "0.908"),
    ("In 3’ UTR variants, only GPN-MSA (0.908) outperformed PhyloP (0.862).", "utr3", "PhyloP", "0.862"),
    ("For 5’ UTR variants, Evo2 (0.767) and GPN-MSA (0.728) surpassed PhyloP (0.696).", "utr5", "Evo2", "0.767"),
    ("For 5’ UTR variants, Evo2 (0.767) and GPN-MSA (0.728) surpassed PhyloP (0.696).", "utr5", "GPN-MSA", "0.728"),
    ("For 5’ UTR variants, Evo2 (0.767) and GPN-MSA (0.728) surpassed PhyloP (0.696).", "utr5", "PhyloP", "0.696"),
    ("For RNA gene variants, GPN-MSA (0.938) again exceeded PhyloP (0.882)", "rna-gene", "GPN-MSA", "0.938"),
    ("For RNA gene variants, GPN-MSA (0.938) again exceeded PhyloP (0.882)", "rna-gene", "PhyloP", "0.882"),
    ("the best performers were AlphaMissense (AUROC=0.959) and PrimateAI-3D (0.943), followed by ESM1b (0.919)", "missense", "AlphaMissense", "0.959"),
    ("the best performers were AlphaMissense (AUROC=0.959) and PrimateAI-3D (0.943), followed by ESM1b (0.919)", "missense", "PrimateAI-3D", "0.943"),
    ("the best performers were AlphaMissense (AUROC=0.959) and PrimateAI-3D (0.943), followed by ESM1b (0.919)", "missense", "ESM1b", "0.919"),
    ("DNA models lagged behind, with GPN-MSA (0.906) coming closest.", "missense", "GPN-MSA", "0.906"),
    ("AlphaMissense (0.849), PrimateAI-3D (0.817), and ESM1b (0.788) all outperformed GPN-MSA (0.783)", "stop-gain", "AlphaMissense", "0.849"),
    ("AlphaMissense (0.849), PrimateAI-3D (0.817), and ESM1b (0.788) all outperformed GPN-MSA (0.783)", "stop-gain", "PrimateAI-3D*", "0.817"),
    ("AlphaMissense (0.849), PrimateAI-3D (0.817), and ESM1b (0.788) all outperformed GPN-MSA (0.783)", "stop-gain", "ESM1b", "0.788"),
    ("AlphaMissense (0.849), PrimateAI-3D (0.817), and ESM1b (0.788) all outperformed GPN-MSA (0.783)", "stop-gain", "GPN-MSA", "0.783"),
    ("leading to GPN-MSA (0.769) and Evo2 (0.711) slightly outperforming the ESM models (0.709)", "start-loss", "GPN-MSA", "0.769"),
    ("leading to GPN-MSA (0.769) and Evo2 (0.711) slightly outperforming the ESM models (0.709)", "start-loss", "Evo2", "0.711"),
    ("leading to GPN-MSA (0.769) and Evo2 (0.711) slightly outperforming the ESM models (0.709)", "start-loss", "ESM2", "0.709"),
    ("AlphaGenome performed best (0.919), followed by Evo2 (0.885) and GPN- MSA (0.882) which surpassed PhyloP (0.855).", "synonymous", "AlphaGenome", "0.919"),
    ("AlphaGenome performed best (0.919), followed by Evo2 (0.885) and GPN- MSA (0.882) which surpassed PhyloP (0.855).", "synonymous", "Evo2", "0.885"),
    ("AlphaGenome performed best (0.919), followed by Evo2 (0.885) and GPN- MSA (0.882) which surpassed PhyloP (0.855).", "synonymous", "GPN-MSA", "0.882"),
    ("AlphaGenome performed best (0.919), followed by Evo2 (0.885) and GPN- MSA (0.882) which surpassed PhyloP (0.855).", "synonymous", "PhyloP", "0.855"),
    ("GPN-MSA (0.888) and Evo2 (0.826) exceeded PhyloP (0.796).", "stop-loss", "GPN-MSA", "0.888"),
    ("GPN-MSA (0.888) and Evo2 (0.826) exceeded PhyloP (0.796).", "stop-loss", "Evo2", "0.826"),
    ("GPN-MSA (0.888) and Evo2 (0.826) exceeded PhyloP (0.796).", "stop-loss", "PhyloP", "0.796"),
]
PROSE_S2 = [("works better (AUROC=0.708) than the composite score based on all modalities (AUROC=0.614)", "splice-outputs-raw", "0.708"),
            ("works better (AUROC=0.708) than the composite score based on all modalities (AUROC=0.614)", "all-outputs-quantile", "0.614"),
            ("an even simpler scorer based just on the raw scores from the splice site usage modality performs even better (AUROC=0.779)", "splice-site-usage-raw", "0.779")]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def flat(s):
    return " ".join(s.split())


def need(text, phrase):
    assert flat(phrase) in text, f"phrase not found: {phrase[:90]}"
    return phrase


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("*", "")).strip("-")


def review(methods, note):
    return {"method": methods, "method_note": note, "reviewer": ["claude"], "reviewer_note": EXTRACTOR_NOTE, "date": TODAY,
            "artifact_sha256": PDF_SHA, "retrieval_url": PDF_URL,
            "note": "Extraction only; pending independent review. The review-evidence pass must re-check this value against the pinned artifact."}


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

    def entity(self, kind, id, name, description, attrs, links=(), method_types=None, contexts=("clinical_research",)):
        facets = {"areas": AREAS, "contexts": list(contexts)}
        if method_types:
            facets["method_types"] = method_types
        return self.add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                         "facets": facets, "source_ids": [S], "links": list(links), "attributes": attrs})

    def claim(self, key, name, subject, field, value, locator, note, limitations=None):
        id = f"{P}-claim-{key}"
        attrs = {"field": field, "value": value, "source_locator": locator, "review": review(["pdf-text-parse", "transcription"], note)}
        if limitations:
            attrs["limitations"] = limitations
        self.rows.append([id, S, locator, value[:200], "claim"])
        return self.add({"id": id, "kind": "claim", "name": name, "description": "Descriptive fact transcribed from the pinned source.",
                         "status": "needs_review", "facets": {}, "source_ids": [S],
                         "links": [{"relation": "subject", "target_id": subject}], "attributes": attrs})


COMMON_AG = ("Official AlphaGenome API (deepmind.google.com/science/alphagenome), 1 Mbp input context centred on the variant, organism human, "
             "all output modalities enabled (5,930 human genomic annotations across 11 modalities).")
AG_CONFIGS = {
    "all-outputs-quantile": ("AlphaGenome all outputs, quantile, maximum (Lu et al. 2025)",
                             "AlphaGenome variant score taken as the maximum quantile (percentile) over all outputs after converting each output to quantiles.",
                             "Recommended implementation: each output converted to quantiles; the variant gets the maximum percentile observed across all outputs, relevant or not to the variant type. Used for every Figure 1 panel."),
    "splice-outputs-raw": ("AlphaGenome splice composite, raw scores (Lu et al. 2025)",
                           "AlphaGenome splice variant score from the original AlphaGenome publication: a weighted sum of raw splice site usage, splice site and splice junction scores.",
                           "Splice variant scorer defined in the original AlphaGenome publication: weighted sum of raw scores from splice site usage, splice site and splice junction outputs. Weights not restated in this paper."),
    "splice-outputs-quantile": ("AlphaGenome splice composite, quantile scores (Lu et al. 2025)",
                                "AlphaGenome splice composite score built from the quantiles of the splice site usage, splice site and splice junction outputs.",
                                "Composite of the three splicing outputs using quantiles; how the three are combined is not stated."),
    "splice-site-usage-raw": ("AlphaGenome splice site usage, raw, maximum (Lu et al. 2025)",
                              "AlphaGenome variant score taken as the maximum raw splice site usage score.",
                              "Splice site usage output only, raw scores, maximum over outputs."),
    "splice-site-usage-quantile": ("AlphaGenome splice site usage, quantile, maximum (Lu et al. 2025)",
                                   "AlphaGenome variant score taken as the maximum quantile of the splice site usage outputs.",
                                   "Splice site usage output only, quantile scores, maximum over outputs."),
    "splice-site-raw": ("AlphaGenome splice site, raw, maximum (Lu et al. 2025)",
                        "AlphaGenome variant score taken as the maximum raw splice site score.", "Splice site output only, raw scores, maximum over outputs."),
    "splice-site-quantile": ("AlphaGenome splice site, quantile, maximum (Lu et al. 2025)",
                             "AlphaGenome variant score taken as the maximum quantile of the splice site outputs.", "Splice site output only, quantile scores, maximum over outputs."),
    "splice-junction-raw": ("AlphaGenome splice junction, raw, maximum (Lu et al. 2025)",
                            "AlphaGenome variant score taken as the maximum raw splice junction score.", "Splice junction output only, raw scores, maximum over outputs."),
    "splice-junction-quantile": ("AlphaGenome splice junction, quantile, maximum (Lu et al. 2025)",
                                 "AlphaGenome variant score taken as the maximum quantile of the splice junction outputs.", "Splice junction output only, quantile scores, maximum over outputs."),
}
OTHER_CONFIGS = {  # row label -> (key, name, description, parameters, method types, locator)
    "Evo2": ("evo2-7b-base-llr", "Evo 2 7B base, 8,192 bp log-likelihood ratio (Lu et al. 2025)",
             "Evo 2 7B base model scoring a variant as the log-likelihood of the alternative minus the reference 8,192 bp sequence.",
             "evo2_7b_base from the Evo2 GitHub repository; 8,192 bp centred window; model.score_sequences on reference and alternative; score multiplied by -1.",
             ["foundation_model"], "Methods 'Evo2' (pages 13 to 14)"),
    "GPN-MSA": ("gpn-msa-precomputed", "GPN-MSA precomputed hg38 scores (Lu et al. 2025)",
                "GPN-MSA precomputed scores for all GRCh38 SNVs from the authors' Hugging Face dataset.",
                "songlab/gpn-msa-hg38-scores scores.tsv.bgz; score multiplied by -1.", ["foundation_model"], "Methods 'GPN-MSA' (page 14)"),
    "PhyloGPN": ("phylogpn-official-example", "PhyloGPN, official example code (Lu et al. 2025)",
                 "PhyloGPN variant scores computed with the official repository's basic example code and a 481 bp context.",
                 "songlab-cal/gpn examples/phylogpn/basic_example.ipynb; 481 bp context (Table 1); score multiplied by -1.",
                 ["foundation_model"], "Methods 'PhyloGPN' (page 14); Table 1"),
    "Nucleotide Transformer": ("nt-2-5b-multispecies-l2", "Nucleotide Transformer 2.5B multi-species, CLS embedding L2 distance (Lu et al. 2025)",
                               "Nucleotide Transformer 2.5B multi-species scoring a variant as the L2 distance between reference and alternative CLS-token embeddings of 6,000 bp sequences.",
                               "InstaDeepAI/nucleotide-transformer-2.5b-multi-species; 6,000 bp context; last hidden layer CLS embeddings; L2 distance.",
                               ["foundation_model"], "Methods 'Nucleotide Transformer' (page 14)"),
    "DNABERT2": ("dnabert2-117m-l2", "DNABERT-2 117M, CLS embedding L2 distance (Lu et al. 2025)",
                 "DNABERT-2 117M scoring a variant as the L2 distance between reference and alternative CLS-token embeddings of 512 bp sequences.",
                 "zhihan1996/DNABERT-2-117M; 512 bp context; last hidden layer CLS embeddings; L2 distance.", ["foundation_model"],
                 "Methods 'DNABERT2' (pages 14 to 15)"),
    "ESM1b": ("esm1b-llr", "ESM1b 650M log-likelihood ratio, Brandes et al. pipeline (Lu et al. 2025)",
              "ESM1b esm1b_t33_650M_UR50S scoring missense variants by the logit difference between alternative and reference residues, with 1,022-residue sliding windows; stop-gains scored by the most deleterious downstream missense score.",
              "esm1b_t33_650M_UR50S; 1,022 aa context, windows with >511 aa overlap combined by weighted sum; start-loss treated as missense; stop-gain = most deleterious possible missense between the stop and the protein end.",
              ["foundation_model"], "Methods 'ESM models' and 'Scoring stop-gain variants by protein models' (page 15)"),
    "ESM1v": ("esm1v-model1-llr", "ESM1v model 1 log-likelihood ratio, Brandes et al. pipeline (Lu et al. 2025)",
              "ESM1v esm1v_t33_650M_UR90S_1 (first of five ensemble members) scoring missense variants by the logit difference between alternative and reference residues.",
              "esm1v_t33_650M_UR90S_1 only; 1,022 aa context; same stop-gain and start-loss handling as ESM1b.", ["foundation_model"],
              "Methods 'ESM models' (page 15)"),
    "ESM2": ("esm2-650m-llr", "ESM2 650M log-likelihood ratio, Brandes et al. pipeline (Lu et al. 2025)",
             "ESM2 esm2_t33_650M_UR50D scoring missense variants by the logit difference between alternative and reference residues.",
             "esm2_t33_650M_UR50D; 1,022 aa context; same stop-gain and start-loss handling as ESM1b.", ["foundation_model"], "Methods 'ESM models' (page 15)"),
    "AlphaMissense": ("alphamissense-precomputed", "AlphaMissense precomputed scores (Lu et al. 2025)",
                      "AlphaMissense precomputed missense scores; stop-gains scored by the most deleterious single-nucleotide-reachable missense score downstream.",
                      "Precomputed scores from alphamissense.hegelab.org; 87 variants with more than one score excluded from missense analyses; stop-gain via RefSeq to UniProt mapping (MyGene) and maximum downstream score.",
                      ["supervised_machine_learning"], "Methods 'AlphaMissense' (page 15)"),
    "PrimateAI-3D": ("primateai-3d-precomputed", "PrimateAI-3D precomputed scores (Lu et al. 2025)",
                     "PrimateAI-3D precomputed missense scores; stop-gains scored by the most deleterious single-nucleotide-reachable missense score downstream.",
                     "Precomputed scores from primateai3d.basespace.illumina.com; for stop-gains 22,613 variants with unmatched isoforms excluded, leaving 19,795.",
                     ["supervised_machine_learning"], "Methods 'PrimateAI-3D' (page 16)"),
    "PhyloP": ("phylop-100way", "PhyloP 100-way vertebrate (Lu et al. 2025)",
               "PhyloP conservation score from the 100-way vertebrate alignment on GRCh38, from the UCSC Genome Browser.",
               "UCSC hg38 phyloP100way precomputed scores.", ["conventional_pipeline"], "Methods 'PhyloP' (page 16)"),
}


def build(b, text):
    b.add({"id": S, "kind": "source",
           "name": "Genomic heterogeneity inflates the performance of variant pathogenicity predictions (Lu, Liu, Lin and Brandes, bioRxiv 2025, v2)",
           "description": "Primary source retrieved and hashed for the 2026-10-19 AlphaGenome variant evidence extraction.",
           "status": "needs_review", "facets": {"areas": AREAS, "contexts": ["clinical_research"]}, "source_ids": [], "links": [],
           "attributes": {
               "url": "https://doi.org/10.1101/2025.09.05.674459", "artifact_url": PDF_URL, "doi": "10.1101/2025.09.05.674459",
               "version": "bioRxiv preprint version 2, posted 2025-09-10 (version 1 posted 2025-09-08); full-text PDF (21 pages)",
               "retrieved_at": RETRIEVED, "artifact_sha256": PDF_SHA, "publication_status": "preprint",
               "licence": "All rights reserved; no reuse allowed without permission (bioRxiv notice)", "media_type": "application/pdf",
               "source_locator": "Results; Figure 1 (page 8); Methods; Supplementary Figures S1 and S2 (pages 20 to 21)",
               "hash_scope": ("SHA-256 of one retrieval of the bioRxiv PDF. bioRxiv stamps the PDF on each download: a second retrieval at "
                              "2026-10-19T12:31:50Z had the same length (1,100,277 bytes), SHA-256 1a1aa1135ad8aa59bdb949bf8df75262eb6feba51b47f49439dbb819c426fbdd, "
                              "differed in 32 bytes (ModDate) and had an identical pdftotext -layout text layer."),
               "limitations": [
                   "Preprint, not peer reviewed. The authors' repository README (Brandes-Lab/VEP-eval, read 2026-10-19, not pinned) names a 2026 Nature Communications version with a rebuilt benchmark (ClinVar February 2026, MANE 1.5) and more models; its DOI did not resolve on 2026-10-19 and it was not extracted.",
                   "Figure 1 and Supplementary Figure S2 have no text layer; their printed labels were transcribed from renders.",
                   "No uncertainty is printed for any AUROC.",
                   "Independent of the AlphaGenome, Evo 2, GPN-MSA and AlphaMissense developers. N. Brandes is an author of the ESM1b variant-effect pipeline reused here for the ESM models.",
                   "Supplementary Table S1 (per-variant scores) was not retrieved.",
               ]}})

    # dataset and protocol
    need(text, "We downloaded the ClinVar16 variant summary file (release: 2025-03-31) and extracted 259,600 single-nucleotide variants")
    d = b.entity("dataset", P + "-data-clinvar-snv-benchmark", "Lu et al. 2025 ClinVar SNV variant-type benchmark (259,600 SNVs)",
                 "ClinVar GRCh38 germline SNVs with definitive pathogenic or benign labels, grouped by variant type from MANE RefSeq and ClinVar HGVS annotations.",
                 {"version": "ClinVar variant_summary release 2025-03-31; MANE RefSeq v1.4 GFF", "variant_count": 259600,
                  "population": "259,600 SNVs (Supplementary Figure S1); 258,944 scored in Figure 1 'All variants', 30.59% pathogenic",
                  "split": "None: all models are zero-shot or precomputed; no training on the benchmark",
                  "repository": "https://github.com/Brandes-Lab/VEP-eval",
                  "source_locator": "Methods 'ClinVar benchmark preparation' (pages 11 to 12); Supplementary Figure S1 (page 20)"})
    need(text, "variants with missing values in any of the compared models were excluded to ensure direct comparison on the same variant set")
    prot = b.entity("protocol", P + "-protocol-clinvar-variant-type-auroc", "ClinVar pathogenic versus benign SNVs within variant type, AUROC (Lu et al. 2025)",
                    "Separate pathogenic from benign ClinVar SNVs within each variant type, scored by AUROC on the variants every compared model scores.",
                    {"metric": "auroc", "metric_direction": "higher",
                     "protocol": ("AUROC per variant group; scores multiplied by -1 where lower means more pathogenic (Evo2, GPN-MSA, PhyloGPN, ESM models); "
                                  "within each group, variants missing a score from any compared model are excluded, except stop-gains for PrimateAI-3D (19,795 of 42,408 scored)."),
                     "source_locator": "Methods 'Calculating and comparing AUROC scores' (pages 12 to 13); Figure 1 legend",
                     "limitations": ["Canonical splice site is defined as intronic within 1 to 2 nt of an exon boundary.",
                                     "Groups such as 'Missense & 3'UTR' hold variants with different effects on different transcripts.",
                                     "No confidence intervals.",
                                     "Benign ClinVar labels can be informed by some of the evaluated predictors; the paper does not address label circularity."]},
                    links=[{"relation": "uses_data", "target_id": d}])
    subsets = {}
    for k, (title, n, pp, _rows) in FIG1.items():
        n_int = int(n.replace(",", ""))
        subsets[k] = b.entity("dataset_subset", f"{P}-subset-{k}", f"Lu et al. 2025 ClinVar benchmark: {title} (Figure 1)",
                              f"ClinVar SNVs in the '{title}' group of the Lu et al. 2025 benchmark, restricted to variants scored by every model in the panel.",
                              {"test_count": n_int, "original_printed_counts": f"N={n}, %P={pp}",
                               "source_locator": f"Figure 1 (page 8), {FIG1_COORD[k]}, title '{title} (N={n}, %P={pp})'",
                               **({"limitations": ["PrimateAI-3D is scored on 19,795 of these variants (Figure 1 footnote and Methods)."]} if k == "stop-gain" else {})},
                              links=[{"relation": "used_in", "target_id": prot}])
    need(text, "Prediction performance (AUROC) over splice variants (N=11,047, %P=99.32%) using different AlphaGenome outputs.")
    subsets["s2"] = b.entity("dataset_subset", f"{P}-subset-splice-figure-s2", "Lu et al. 2025 ClinVar benchmark: splice variants scored by AlphaGenome (Supplementary Figure S2)",
                             "ClinVar canonical splice-site SNVs (within 1 to 2 nt of an exon boundary) scored by the AlphaGenome scorers compared in Supplementary Figure S2.",
                             {"test_count": 11047, "original_printed_counts": "N=11,047, %P=99.32%",
                              "source_locator": "Supplementary Figure S2 legend (page 21)",
                              "limitations": ["Figure 1 'Splice' has N=11,042; the five-variant difference is not explained, so the two splice AUROCs for the all-outputs scorer (0.592 and 0.614) are on different variant sets."]},
                             links=[{"relation": "used_in", "target_id": prot}, {"relation": "same_data_as", "target_id": f"{P}-subset-splice"}])

    # configurations
    need(text, "To calculate variant effect scores, we used the recommended implementation, which converts each output to quantiles and assigns variants the maximum percentile observed across all outputs.")
    need(text, "which takes a weighted sum of raw scores from the three splice-related modalities (splice site usage, splice site, and splice junction)")
    cfg = {}
    for key, (name, desc, params) in AG_CONFIGS.items():
        cfg["AlphaGenome:" + key] = b.entity("configuration", f"{P}-config-alphagenome-{key}", name, desc,
                                             {"reported_name": "AlphaGenome" if key == "all-outputs-quantile" else next(l for l, _, k in FIGS2 if k == key),
                                              "parameters": COMMON_AG + " " + params,
                                              "access_reuse": "Official AlphaGenome API",
                                              "source_locator": "Methods 'AlphaGenome' (pages 16 to 17); Supplementary Figure S2",
                                              "missing_metadata": {"model_version": {"reason": "unreported", "note": "API model version and query date not printed."}}},
                                             links=[{"relation": "configuration_of", "target_id": MODELS["AlphaGenome"]}], method_types=["foundation_model"])
    for label, (key, name, desc, params, mt, loc) in OTHER_CONFIGS.items():
        cfg[label] = b.entity("configuration", f"{P}-config-{key}", name, desc,
                              {"reported_name": label, "parameters": params, "source_locator": loc},
                              links=[{"relation": "configuration_of", "target_id": MODELS[label]}], method_types=mt)
    cfg["PrimateAI-3D*"] = cfg["PrimateAI-3D"]
    need(text, "we constructed a rule-based baseline assigning each variant a score equal to the frequency of pathogenic variants within its type.")
    rule_m = b.entity("method", P + "-method-variant-type-prior", "Variant-type pathogenicity prior",
                      "Scores each variant by the fraction of pathogenic variants among labelled variants of its type.",
                      {"entity_level": "method", "reported_name": "Rule-based",
                       "source_locator": "Results paragraph 2 (page 6)"}, method_types=["conventional_pipeline"])
    cfg["Rule-based"] = b.entity("configuration", P + "-config-variant-type-prior", "Variant-type pathogenicity prior on the benchmark's own labels (Lu et al. 2025)",
                                 "Assigns each variant the frequency of pathogenic variants within its variant type, computed from the benchmark labels.",
                                 {"reported_name": "Rule-based", "training_overlap": "Uses the benchmark's own labels to compute the per-type prior; an upper reference for type-only information, not a fair predictor.",
                                  "source_locator": "Results paragraph 2 (page 6)"},
                                 links=[{"relation": "configuration_of", "target_id": rule_m}], method_types=["conventional_pipeline"])

    # Figure 1 evaluations and results
    fig = {(k, row): v for k, (_, _, _, rows) in FIG1.items() for row, v in rows}
    for sentence, k, row, v in PROSE:
        need(text, sentence)
        assert fig[(k, row)] == v, (k, row, fig[(k, row)], v)
    prose_by_cell = {}
    for sentence, k, row, v in PROSE:
        prose_by_cell.setdefault((k, row), sentence)
    for k, (title, n, pp, rows) in FIG1.items():
        for row, printed in rows:
            sys_id = cfg["AlphaGenome:all-outputs-quantile"] if row == "AlphaGenome" else cfg[row]
            rk = slug(row)
            loc = f"Figure 1 (page 8), {FIG1_COORD[k]} '{title} (N={n}, %P={pp})', row '{row}', bar label"
            ev = b.evaluation(f"{P}-eval-{k}-{rk}", f"{row} on ClinVar {title} SNVs (Lu et al. 2025 Figure 1)", sys_id, prot, subsets[k],
                              title, n, pp, loc, stop_gain_primateai=(row == "PrimateAI-3D*"))
            note = ("Bar label transcribed from a 400 dpi render of page 8 (the figure has no text layer); row order asserted in extract/build_batch.py.")
            if (k, row) in prose_by_cell:
                note += f" The text prints the same value: '{prose_by_cell[(k, row)]}' (asserted)."
            extra = {}
            if k in ("all-variants", "noncoding"):
                extra["limitations"] = ["Pooled over heterogeneous variant types; the paper shows that pooled AUROC is inflated by differences in pathogenic prevalence between types."]
            if row == "PrimateAI-3D*":
                extra["limitations"] = ["Scored on 19,795 of the 42,408 stop-gain variants only (Figure 1 footnote)."]
            b.result(f"{P}-result-{k}-{rk}-auroc", f"{row} AUROC, ClinVar {title}", ev, printed, loc,
                     ["rendered-source-visual-check", "transcription"] + (["pdf-text-parse"] if (k, row) in prose_by_cell else []),
                     note, f"ClinVar pathogenic vs benign SNVs, {title}", extra)

    # Supplementary Figure S2
    s2 = {k: v for _, v, k in FIGS2}
    for sentence, k, v in PROSE_S2:
        need(text, sentence)
        assert s2[k] == v, (k, s2[k], v)
    for label, printed, key in FIGS2:
        loc = f"Supplementary Figure S2 (page 21), row '{label}', bar label"
        ev = b.evaluation(f"{P}-eval-splice-s2-alphagenome-{key}", f"AlphaGenome {label} on ClinVar splice variants (Lu et al. 2025 Supplementary Figure S2)",
                          cfg["AlphaGenome:" + key], prot, subsets["s2"], "Splice (Supplementary Figure S2)", "11,047", "99.32%", loc)
        note = "Bar label transcribed from a 200 dpi render of page 21 (the figure is a raster image)."
        hit = [s for s, k2, _ in PROSE_S2 if k2 == key]
        if hit:
            note += f" The Methods text prints the same value: '{hit[0]}' (asserted)."
        b.result(f"{P}-result-splice-s2-alphagenome-{key}-auroc", f"AlphaGenome {label} AUROC, ClinVar splice variants", ev, printed, loc,
                 ["rendered-source-visual-check", "transcription"] + (["pdf-text-parse"] if hit else []), note,
                 f"ClinVar pathogenic vs benign canonical splice SNVs (N=11,047); AlphaGenome scorer '{label}'", {})

    # claims
    need(text, "Notably, AlphaGenome is highly sensitive to the specific method used to extract scores from the model, which may be partly responsible for its highly unstable performance (see Methods).")
    b.claim("alphagenome-scorer-sensitivity", "AlphaGenome results depend on the scoring method", MODELS["AlphaGenome"], "evaluation_finding",
            ("Lu et al. report that AlphaGenome is highly sensitive to the method used to extract scores: with the recommended all-output maximum-quantile score it "
             "ranks first on non-splice intronic (0.960) and synonymous (0.919) ClinVar SNVs but reaches 0.592 on canonical splice SNVs, where the raw splice site "
             "usage score reaches 0.779 and the original publication's splice scorer 0.708 (Supplementary Figure S2)."),
            "Discussion paragraph 1 (page 10); Methods 'AlphaGenome' (pages 16 to 17); Figure 1; Supplementary Figure S2",
            "Statement asserted in the pdftotext -layout text; numbers asserted against the figure transcription.")
    b.claim("alphagenome-scoring-setup", "AlphaGenome scoring setup in Lu et al. 2025", cfg["AlphaGenome:all-outputs-quantile"], "scoring_setup", COMMON_AG +
            " Each output converted to quantiles; the variant score is the maximum percentile across all outputs.",
            "Methods 'AlphaGenome' (pages 16 to 17)", "Sentences asserted in the pdftotext -layout text.")
    b.claim("figures-transcribed", "Lu et al. 2025 values read from figure labels", S, "extraction_method",
            ("Figure 1 and Supplementary Figure S2 are the only places most values are printed. Figure 1 is vector art without a text layer and S2 is a raster "
             "image; every bar carries a printed numeric label and a named row, so the labels were transcribed from renders. Figure 2 (Evo2 score distributions) "
             "has no printed values and is not extracted."),
            "Figure 1 (page 8); Figure 2 (page 9); Supplementary Figure S2 (page 21)", "Scope decision recorded by the extractor.")


def evaluation(self, id, name, system, protocol, data, title, n, pp, loc, stop_gain_primateai=False):
    comparison = {"protocol_id": protocol, "dataset_version": "ClinVar variant_summary 2025-03-31; MANE RefSeq v1.4",
                  "split": "None: zero-shot or precomputed scores", "population": f"ClinVar SNVs, {title} (N={n}, %P={pp})" +
                  ("; PrimateAI-3D scored on 19,795 variants" if stop_gain_primateai else ""),
                  "inputs": "Reference and alternative sequence or precomputed score per variant",
                  "adaptation": "None", "metric_implementation": "AUROC on scores oriented so higher means more pathogenic",
                  "aggregation": "One AUROC per variant group on variants scored by every compared model", "budget": None}
    attrs = {"origin": "independent_paper", "protocol": protocol, "version": "bioRxiv v2, retrieved " + TODAY, "comparison": comparison,
             "source_locator": loc,
             "missing_metadata": {"comparison.budget": {"reason": "inapplicable", "note": "Zero-shot or precomputed scoring; no budget."}}}
    return self.entity("evaluation", id, name, "Independent comparison transcribed from the pinned source; not reproduced.", attrs,
                       links=[{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
                              {"relation": "data", "target_id": data}])


def result(self, id, name, evaluation, printed, loc, methods, note, qualifier, extra):
    attrs = {"metric": "auroc", "metric_direction": "higher", "unit": "unitless", "printed_value": printed, "numeric_value": printed,
             "metric_qualifier": qualifier, "source_locator": loc, "missing_metadata": {"uncertainty": {"reason": "unreported"}},
             "review": review(methods, note)}
    assert re.fullmatch(r"\d\.\d{3}", printed), printed
    attrs.update(extra)
    self.rows.append([id, S, loc, printed, "result"])
    return self.add({"id": id, "kind": "result", "name": name,
                     "description": "Independent value transcribed from the pinned source. Not reproduced.",
                     "status": "needs_review", "facets": {}, "source_ids": [S],
                     "links": [{"relation": "evaluation", "target_id": evaluation}], "attributes": attrs})


Batch.evaluation = evaluation
Batch.result = result


def main(art, out):
    path = os.path.join(art, PDF)
    assert sha256(path) == PDF_SHA, "artifact hash mismatch"
    layout = subprocess.run(["pdftotext", "-layout", path, "-"], check=True, capture_output=True, text=True).stdout
    # Drop the manuscript line numbers printed in the margin, and the repeated bioRxiv page header, so sentences read through.
    layout = re.sub(r"(?m)^\s*\d{1,3}(?:\s{2,}|$)", "", layout)
    layout = re.sub(r"(?m)^\s*bioRxiv preprint doi:.*\n.*No reuse allowed without permission\.\s*$", "", layout)
    text = flat(layout)
    b = Batch()
    build(b, text)
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
