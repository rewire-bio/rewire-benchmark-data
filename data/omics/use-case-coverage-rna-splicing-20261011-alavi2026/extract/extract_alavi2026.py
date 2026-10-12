"""Extract Alavi 2026 (bioRxiv 10.64898/2026.10.02.756289 v1) Tables III and IV into batch records.

Usage: python3 -I extract_alavi2026.py <full.pdf> <batch folder>
bioRxiv stamps the PDF on each serving, so the pinned bytes cannot be re-downloaded and are not archived (CC BY-NC-ND).
The script also accepts the reviewer's 2026-10-12 retrieval (REVIEW_SHA, same length; see hash_scope), which gives
byte-identical output; records stay bound to the pinned SHA.
Runs `pdftotext -layout` (poppler 26.08.0 was used) on the pinned PDF, finds the value rows of Table III (8 cells per
row) and Table IV (6 cells per row) by token pattern, asserts 12 rows per table and the row-label fragments between
them, checks counts against percentages, and writes needs_review records. Cells print a count with the percentage
in brackets; numeric_value is the percentage.
"""
import json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalize_review, judgement, refresh_coverage, sha256

PDF, OUT = sys.argv[1], sys.argv[2]
SHA = "e11f4bd8818992a831cb2829d934287c2587b108881c9785c2ef5c8cdc730004"
URL = "https://www.biorxiv.org/content/10.64898/2026.10.02.756289v1.full.pdf"
REVIEW_SHA = "e22491e217c7c158528668b38bcb8b9855b89617b807c60b740795a204c84b0a"
assert sha256(PDF) in (SHA, REVIEW_SHA)
text = subprocess.run(["pdftotext", "-layout", PDF, "-"], capture_output=True, text=True, check=True).stdout.split("\n")

P = "rna-splicing-20261011-alavi2026"
b = Batch(OUT, P, areas=["dna-genomes"])
SRC = P + "-source-article"
UC = "use-case-patient-rna-splicing-validation"
UC_NAME = "Select a patient-RNA splicing-variant validation workflow"

b.source(SRC, "Probing Genomic Foundation Models with Splice-Variant Perturbations (Alavi, bioRxiv 2026)", {
    "url": "https://doi.org/10.64898/2026.10.02.756289",
    "artifact_url": URL,
    "version": "bioRxiv preprint version 1, posted 2026-10-09; full-text PDF (11 pages)",
    "retrieved_at": "2026-10-11T21:42:49Z",
    "artifact_sha256": SHA,
    "doi": "10.64898/2026.10.02.756289",
    "publication_status": "preprint",
    "licence": "CC-BY-NC-ND-4.0",
    "media_type": "application/pdf",
    "limitations": [
        "Preprint, not peer reviewed; single author (712 North Inc.), no funding; none of the evaluated models was developed by the author.",
        "The bioRxiv JATS XML holds metadata only, so the tables were read from the PDF text layer.",
        "Supplementary Tables I to VI and the Zenodo material (doi.org/10.5281/zenodo.23105803) were not retrieved.",
        "Table IV prints 15 (13.9%) for AlphaGenome splice scorer and 31 (28.7%) for Genos 10B ClinVar type I errors; 15/107 is 14.0% and 31/107 is 29.0%.",
        "Not archived in the batch: CC BY-NC-ND licence; hash and locators only.",
        # review correction 3
        "Four printed accuracies differ from those computed from the same row's counts: Table III Borzoi (128-bp) 89.1% (counts give 89.8%); Table IV AlphaGenome (either module) 71.6% (70.5%), Borzoi (128-bp) 80.9% (81.4%) and Genos 10B 61.7% (61.2%).",
    ],
    # review correction 4
    "hash_scope": "SHA-256 of one retrieval of the bioRxiv PDF. bioRxiv stamps the PDF when serving it (ModDate and the second document ID), so later retrievals differ. A reviewer retrieval on 2026-10-12 of the same length (1,823,372 bytes) had SHA-256 e22491e217c7c158528668b38bcb8b9855b89617b807c60b740795a204c84b0a and ModDate D:20261011221204-07'00'. All 168 Table III and IV cells in that copy match the stored results.",
    "retrieval_note": "bioRxiv returned HTTP 429 (rate limit) on earlier attempts the same evening; the PDF request succeeded on its first try.",
})

TOK = re.compile(r"\d+ \(\d+(?:\.\d+)? ?%\)|\d+(?:\.\d+)?%")
LABELS = [  # printed label (joined), config key, model id, method type, foundation model, version, parameters, access
    ("SPLICEAI", "spliceai", "catalog-model-spliceai", "supervised_machine_learning", False, "Broad Institute SpliceAI-lookup API v1.3.1",
     "Unmasked delta scores in a 1,000 bp interval (±500 bp); maximum of the four delta scores; threshold > 0.40 by grid search on the OPA1 evaluation sets", "Public API (SpliceAI-lookup)"),
    ("ALPHAGENOME (EITHER MODULE)", "alphagenome-either-module", "catalog-model-alphagenome", "supervised_machine_learning", False, "Google Cloud API (research access), version not printed",
     "Positive if either the splice-site module (>= 0.14) or the splice-junction module (>= 0.43) is positive", "Google DeepMind Research Access program API"),
    ("ALPHAGENOME SPLICE SCORER", "alphagenome-splice-scorer", "catalog-model-alphagenome", "supervised_machine_learning", False, "Google Cloud API (research access), version not printed",
     "GeneMaskSplicingScorer; maximum absolute probability change over acceptor, donor, intronic and exonic sites within ±500 bp of a 1 Mb window; threshold >= 0.14", "Google DeepMind Research Access program API"),
    ("ALPHAGENOME JUNCTION SCORER", "alphagenome-junction-scorer", "catalog-model-alphagenome", "supervised_machine_learning", False, "Google Cloud API (research access), version not printed",
     "SpliceJunctionScorer; absolute peak junction delta within ±65,536 bp; threshold >= 0.43", "Google DeepMind Research Access program API"),
    ("BORZOI (32-BP)", "borzoi-32-bp", "regulatory-variant-20261009-model-borzoi", "supervised_machine_learning", False, "Flashzoi implementation, johahi/borzoi-replicate-0 to -3",
     "Ensemble of four replicates; 22 ENCODE plus-strand tracks averaged; strand-averaged log-fold change in the central 32-bp bin; LFC <= -0.14 or > +0.24", "Public weights (Hugging Face)"),
    ("BORZOI (128-BP)", "borzoi-128-bp", "regulatory-variant-20261009-model-borzoi", "supervised_machine_learning", False, "Flashzoi implementation, johahi/borzoi-replicate-0 to -3",
     "As 32-bp but at 128-bp resolution; LFC <= -0.10 or > +0.19", "Public weights (Hugging Face)"),
    ("NTV3 650M POST", "ntv3-650m-post", "lit-genomics-20261011-guanine-model-nucleotide-transformer-v3", "foundation_model", True, "InstaDeepAI/NTv3_650M_post",
     "Zero-shot log-likelihood ratio, 16,384 bp context, human species embedding, summed over ±16 bp; forward and reverse strands; thresholds by grid search (Methods F)", "Public weights (Hugging Face)"),
    ("NTV3 650M PRE", "ntv3-650m-pre", "lit-genomics-20261011-guanine-model-nucleotide-transformer-v3", "foundation_model", True, "InstaDeepAI/NTv3_650M_pre",
     "Zero-shot log-likelihood ratio, 16,384 bp context, summed over ±16 bp; forward and reverse strands; thresholds by grid search (Methods F)", "Public weights (Hugging Face)"),
    ("EVO2 40B (W/O HU. IDENT.)", "evo2-40b-without-human-identifier", "catalog-model-evo-2", "foundation_model", True, "NVIDIA NIM evo2-40b:2.0.0",
     "Zero-shot next-token log-likelihood ratio at the variant from a 425 bp upstream prefix, both strands; no taxonomic prefix; LLR fwd <= -5.34 or rev <= -7.03", "NVIDIA API catalog microservice"),
    ("EVO2 40B (HU. IDENT.)", "evo2-40b-human-identifier", "catalog-model-evo-2", "foundation_model", True, "NVIDIA NIM evo2-40b:2.0.0",
     "As without identifier, but the prefix is prepended with a human taxonomic identifier; LLR fwd <= -5.69 or rev <= -5.55", "NVIDIA API catalog microservice"),
    ("GENOS 10B", "genos-10b", None, "foundation_model", True, "ZhejiangLab/Genos-10B (the v2 iteration is reported only in Supplementary Table III)",
     "Zero-shot summed log-likelihood ratio over a 4,096 bp downstream readout from a 94,208 bp upstream window, both strands; LLR fwd <= -60.57 or rev <= -98.94", "Public weights (Hugging Face)"),
    ("GENOS 10B CLINVAR", "genos-10b-clinvar", None, "foundation_model", True, "Zhejiang Lab ClinVar-based probability API (version not printed)",
     "ClinVar-trained pathogenicity probability from the Zhejiang Lab API (DCS Cloud); threshold >= 0.63", "Zhejiang Lab API through the DCS Cloud catalog"),
]
GENOS = "lit-microbial-20261011-virobench-model-genos"  # review correction 1: existing Genos family record, not a duplicate


def display(name):  # review correction 2: name casing
    for old, new in (("Alphagenome", "AlphaGenome"), ("Spliceai", "SpliceAI"), ("Ntv3", "NTv3"), ("Clinvar", "ClinVar"), ("-Bp)", "-bp)"),
                     ("(W/O Hu. Ident.)", "(without human identifier)"), ("(Hu. Ident.)", "(human identifier)")):
        name = name.replace(old, new)
    return name


CFG = {}
for label, key, model, mt, fm, version, params, access in LABELS:
    CFG[label] = b.rid("config", key)
    b.entity("configuration", CFG[label], display(f"{label.title()} (Alavi 2026)"), f"{label} as configured in Alavi 2026.", [SRC], {
        "reported_name": label, "foundation_model_eligible": fm, "version": version, "parameters": params, "access_reuse": access,
        "source_locator": "Methods C to H; Table III and IV row label",
        **({"fine_tuning": {"applied": True, "note": "ClinVar-based pathogenicity probability from the Zhejiang Lab API; training details not printed (Methods H)"}} if key == "genos-10b-clinvar" else {}),
    }, method_types=[mt], links=[{"relation": "configuration_of", "target_id": model or GENOS}])


def rows_for(table, ncells):
    i = [k for k, l in enumerate(text) if l.strip() == table][0]
    out, start = [], i
    for k in range(i, i + 60):
        v = TOK.findall(text[k])
        if len(v) == ncells:
            out.append((k, v))
    assert len(out) == 12, (table, len(out))
    # every printed label fragment lies between the previous value row and the next one
    prev = i
    for (k, v), lab in zip(out, LABELS):
        nxt = out[out.index((k, v)) + 1][0] if (k, v) != out[-1] else k + 4
        window = " ".join(text[prev + 1:nxt]).upper()
        for frag in lab[0].replace("(", " ").replace(")", " ").split():
            assert frag in window, (table, lab[0], frag)
        prev = k
    return out


DATA = {
    "opa1-evaluation-sets": ("OPA1 LOVD evaluation sets (49 splicing, 79 benign)", "49 OPA1 single-nucleotide substitutions annotated 'consequence: splicing defect' and 79 benign or likely benign substitutions from LOVD (retrieved 2026-04-15), GRCh38, NM_015560.2",
                             "Methods A 'Dataset selection and curation'; Table I"),
    "opa1-extended-corpus": ("OPA1 extended LOVD corpus (306 pathogenic substitutions, 69 VUS)", "OPA1 LOVD substitutions outside the evaluation sets: 306 pathogenic or likely pathogenic mutations and 69 variants of uncertain significance, without splicing labels",
                             "Results D 'Positional Variant classification across the OPA1 corpus'; Table III header"),
    "multigene": ("Multi-gene spliceogenic test set (76 spliceogenic, 107 benign, 65 genes)", "76 functionally validated spliceogenic substitutions at canonical splice sites of 65 genes from Bournazos et al. 2022 (RNA diagnostics in clinically accessible specimens) and Dawes et al. 2023 (SpliceVault), with 107 high-confidence ClinVar benign intronic substitutions from 46 of the 65 genes",
                  "Methods A; Results F 'Multi-gene benchmarking'; references 13 and 14"),
}
DID = {}
for key, (name, pop, loc) in DATA.items():
    DID[key] = b.rid("data", key)
    b.entity("dataset", DID[key], name, f"{name} as assembled by Alavi 2026.", [SRC],
             {"version": "As assembled by Alavi 2026", "population": pop, "split": "No split", "source_locator": loc})

COMMON = ["Thresholds were set by one-dimensional grid search on the OPA1 evaluation sets, optimising accuracy and specificity (Methods B).",
          "Single-author preprint; no uncertainty intervals are printed for the tabulated metrics.",
          "Foundation-model scores are zero-shot log-likelihood ratios with author-chosen context windows, aggregation and strand rules (Methods F to H)."]
PROTS = {
    "opa1-evaluation": dict(table="TABLE III", cols=list(range(6)), data="opa1-evaluation-sets",
        name="Splice-defect classification of OPA1 variants with thresholds tuned on the same sets (Alavi Table III, evaluation sets)",
        protocol="Classify the 49 OPA1 splicing-defect and 79 benign substitutions with each model at its grid-searched threshold; report accuracy, PPV, type I error (false positives / benign set), specificity, sensitivity and type II error (false negatives / splicing set).",
        locator="Table III columns 'Accuracy' to 'Type II error'; Methods B and I; Equations 1 to 5",
        limits=["In-sample: thresholds were optimised on these 128 variants, so the values are optimistic.", "Positives are LOVD entries annotated as splicing defects; the assay behind each annotation is not stated."]),
    "opa1-extended-positive-calls": dict(table="TABLE III", cols=[6, 7], data="opa1-extended-corpus",
        name="Share of further OPA1 pathogenic substitutions and VUS called splice-altering (Alavi Table III, extended corpus)",
        protocol="Apply the OPA1-tuned thresholds to 306 pathogenic substitutions and 69 VUS outside the evaluation sets and report the count and share called positive.",
        locator="Table III columns 'Positive mutations' and 'Positive VUS'; Results D",
        limits=["No splicing labels: a positive call rate is not an accuracy measure."]),
    "multigene": dict(table="TABLE IV", cols=list(range(6)), data="multigene",
        name="Spliceogenic versus benign classification on an independent 65-gene set with OPA1-derived thresholds (Alavi Table IV)",
        protocol="Apply the OPA1-tuned thresholds unchanged to 76 spliceogenic and 107 benign substitutions in 65 genes; report accuracy, PPV, type I error, specificity, sensitivity and type II error.",
        locator="Table IV; Methods A; Results F 'Multi-gene benchmarking'",
        limits=["Spliceogenic positives are canonical splice-site substitutions only; benign controls are ClinVar intronic substitutions from 46 of the 65 genes.",
                "Positives were confirmed by RNA studies in the cited sources (references 13 and 14); this preprint does not restate the assay per variant."]),
}
COLS3 = ["Accuracy", "PPV", "Type I error", "Specificity", "Sensitivity", "Type II error", "Positive mutations", "Positive VUS"]
COLMETRIC = {  # column: metric, direction, qualifier, unit_detail, denominator key
    "Accuracy": ("accuracy", "higher", None, None, None),
    "PPV": ("precision", "higher", None, None, None),
    "Type I error": ("false-positive-rate", "lower", "type I error: false positives as a share of the benign set", "Cell prints the count of false positives with the percentage of the benign set in brackets; numeric_value is the percentage", "benign"),
    "Specificity": ("specificity", "higher", None, "Cell prints the count of true negatives with the percentage in brackets; numeric_value is the percentage", "benign"),
    "Sensitivity": ("recall", "higher", None, "Cell prints the count of true positives with the percentage in brackets; numeric_value is the percentage", "splicing"),
    "Type II error": ("proportion", "lower", "type II error: false negatives as a share of the splicing set (false-negative rate)", "Cell prints the count of false negatives with the percentage of the splicing set in brackets; numeric_value is the percentage", "splicing"),
    "Positive mutations": ("proportion", "unknown", "share of 306 further OPA1 pathogenic substitutions called splice-altering", "Cell prints the count called positive with the percentage of 306 in brackets; numeric_value is the percentage", "mutations"),
    "Positive VUS": ("proportion", "unknown", "share of 69 OPA1 VUS substitutions called splice-altering", "Cell prints the count called positive with the percentage of 69 in brackets; numeric_value is the percentage", "vus"),
}
N = {"TABLE III": {"benign": 79, "splicing": 49, "mutations": 306, "vus": 69}, "TABLE IV": {"benign": 107, "splicing": 76}}
METHOD_NOTE = ("pdftotext -layout (poppler 26.08.0) on the pinned PDF; value rows found by token pattern, 12 rows per table and "
               "row-label fragments between rows asserted; printed cell text kept exactly; bracketed percentages checked against counts.")
# review correction 5
GENOS_CLINVAR = "Genos 10B ClinVar is fine-tuned on ClinVar labels and the benign controls are ClinVar variants; training overlap is not tested in the source."
mismatches = []
tables = {"TABLE III": rows_for("TABLE III", 8), "TABLE IV": rows_for("TABLE IV", 6)}
links = []
for pkey, p in PROTS.items():
    prot = b.rid("protocol", pkey)
    b.entity("protocol", prot, p["name"], p["protocol"], [SRC], {
        "protocol": p["protocol"], "version": p["table"].replace("TABLE", "Table"), "source_locator": p["locator"],
        "limitations": p["limits"] + COMMON + ([GENOS_CLINVAR] if pkey == "multigene" else []),
    }, links=[{"relation": "uses_data", "target_id": DID[p["data"]]}])
    tnum = "III" if p["table"] == "TABLE III" else "IV"
    for (line, cells), lab in zip(tables[p["table"]], LABELS):
        label, key = lab[0], lab[1]
        ev = b.rid("eval", pkey, key)
        b.evaluation(ev, display(f"{label.title()} on {DATA[p['data']][0]}"), [SRC], CFG[label], prot, DID[p["data"]], "independent_paper", {
            "dataset_version": "As assembled by Alavi 2026", "split": "No split", "population": DATA[p["data"]][1],
            "inputs": "Single-nucleotide variant with genomic sequence context (GRCh38)",
            "adaptation": "zero-shot scores with thresholds grid-searched on the OPA1 evaluation sets",
            "metric_implementation": "Equations 1 to 5 (type I error, type II error, accuracy, specificity, sensitivity); PPV",
            "aggregation": "Whole set", "budget": None,
        }, f"Table {tnum} row '{label}'")
        for ci in p["cols"]:
            col = COLS3[ci] if p["table"] == "TABLE III" else COLS3[:6][ci]
            cell = cells[ci]
            metric, direction, qual, udet, den = COLMETRIC[col]
            m = re.fullmatch(r"(\d+) \((\d+(?:\.\d+)?) ?%\)", cell)
            if m:
                numeric = m.group(2)
                expect = 100 * int(m.group(1)) / N[p["table"]][den]
                if abs(expect - float(numeric)) > 0.051:
                    mismatches.append(f"Table {tnum} '{label}' {col}: {cell} vs {expect:.2f}%")
            else:
                numeric = cell.rstrip("%")
            b.result(b.rid("result", pkey, key, col.lower().replace(" ", "-")), display(f"{label.title()} {col} (Alavi Table {tnum})"),
                     SRC, [SRC], ev, cell, metric, direction, "percent", f"Table {tnum}, row '{label}', column '{col}' (PDF page {6 if tnum == 'III' else 9} of 11)",
                     extraction_review(["pdf-text-parse"], METHOD_NOTE, SHA, URL), qualifier=qual, unit_detail=udet, numeric=numeric)
    if pkey != "opa1-extended-positive-calls":
        cid, _ = judgement(
            b, UC, UC_NAME, prot, p["name"], [SRC], [{"source_id": SRC, "locator": p["locator"]}], "proxy",
            "Accuracy, PPV, specificity, sensitivity and error rates of SpliceAI, AlphaGenome, Borzoi and the genomic foundation models NTv3 650M, Evo2 40B and Genos 10B on " + DATA[p["data"]][0],
            "Proxy: DNA-sequence models, including genomic foundation models, classify variants with established splicing defects against benign variants; this is the sequence-classification kind of evidence, not recovery of events in patient RNA-seq.",
            ["Inspect every linked evaluation's source locator before citing a result.",
             "Do not combine this mapping's evaluations with any other protocol's results; variant sets and thresholds differ."],
            p["limits"] + COMMON + ["Preprint (bioRxiv v1), not peer reviewed."] + ([GENOS_CLINVAR] if pkey == "multigene" else []),
            "accuracy", "alavi2026-opa1-splice-variants", "Splice predictors and genomic foundation models on OPA1 and multi-gene splice variants (Alavi 2026)",
            "OPA1 evaluation sets (thresholds tuned here)" if pkey == "opa1-evaluation" else "Independent 65-gene test set", 1 if pkey == "opa1-evaluation" else 2,
            "Recorded from the 2026-10-11 use-case literature pass (data/omics/use-case-coverage-rna-splicing-20261011-alavi2026); pending independent review.")
        links.append({"use_case": UC, "relation": "assessed_by", "target_id": prot, "judgement_claim": cid})

assert mismatches == ["Table IV 'ALPHAGENOME SPLICE SCORER' Type I error: 15 (13.9%) vs 14.02%",
                      "Table IV 'GENOS 10B CLINVAR' Type I error: 31 (28.7%) vs 28.97%"], mismatches
finalize_review(b, {  # reviewed_evaluations: the 12 evaluations on each judged protocol
    "use-case-mapping-" + P + "-" + k: [P + "-eval-" + k + "-" + lab[1] for lab in LABELS] for k in ("opa1-evaluation", "multigene")},
    method=["pdf-text-parse", "independent-cell-check", "automated-source-review"])
counts = b.write({"use-case-links.json": json.dumps({"note": "Proposed assessed_by links to add to the use_case record after the judgement claims are reviewed. Not applied by the extractor.", "links": links}, indent=1) + "\n"})
refresh_coverage(OUT)
print(json.dumps(counts))
