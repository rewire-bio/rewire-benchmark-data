"""GUANinE v1.1 (Robson and Ioannidis, Bioinformatics 2026): Tables 2, 3 and 4 from the PMC XML.

Usage: python3 -I extract_guanine.py <fulltext.xml> <batch-folder>
"""
import sys, os, re, json
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, slug, num

xml_path, folder = sys.argv[1], sys.argv[2]
SHA = sha256(xml_path)
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13501288/fullTextXML"
assert SHA == "f6cc4294a1519fb5579eebb29ffd919afad0198a3bf8b751635d73b17b33ef79", SHA

b = Batch(folder, "lit-genomics-20261011-guanine")
SRC = b.source("lit-genomics-20261011-guanine-source-robson2026", "GUANinE v1.1 reveals complementarity of supervised and genomic language models", {
    "url": "https://doi.org/10.1093/bioinformatics/btag427", "artifact_url": URL,
    "version": "Bioinformatics 2026, btag427 (issue date 2026-08-01); PMC13501288 full-text XML",
    "retrieved_at": "2026-10-11T00:40:24Z", "artifact_sha256": SHA, "doi": "10.1093/bioinformatics/btag427",
    "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml",
    "limitations": ["The XML does not carry the blue colouring that Table 2 uses to mark previously reported performances, so which Table 2 cells repeat earlier GUANinE results cannot be told from this artifact.",
                    "The supplementary PDF (btag427_supplementary_data.pdf) is a scanned print with no text layer and was not read."]})
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["deterministic-table-parse"],
    "Parsed the <td> cells of the pinned PMC XML table with tools/extract_guanine.py; row label and column header taken from the same table row and header rows. " + loc,
    SHA, URL)

root = ET.fromstring(open(xml_path, "rb").read())
tables = {}
for tw in root.iter("table-wrap"):
    lab = " ".join("".join(tw.find("label").itertext()).split())
    rows = [[" ".join("".join(c.itertext()).split()) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    tables[lab] = rows

# Model families: reuse existing store records where the family exists.
EXISTING = {
    "Enformer": "regulatory-variant-20261009-model-enformer", "Borzoi": "regulatory-variant-20261009-model-borzoi",
    "Sei": "regulatory-variant-20261009-model-sei", "ChromBPNet": "discovery-model-chrombpnet",
    "Caduceus": "regulatory-variant-20261009-model-caduceus", "DNABERT-2": "discovery-model-dnabert-2",
    "GENA-LM": "regulatory-variant-20261009-model-gena-lm", "Evo 2": "discovery-model-evo-2",
    "Nucleotide Transformer v2": "catalog-model-nt-v2", "GPN": "regulatory-variant-20261009-model-gpn",
    "AlphaGenome": "catalog-model-alphagenome", "Pangolin": "discovery-model-pangolin",
    "DeepSEA": "bend-method-deepsea", "CADD": "somatic-oncogenicity-20261009-method-cadd",
    "phyloP": "somatic-oncogenicity-20261009-method-phylop",
}
NEW_MODELS = {  # family name -> (kind, description, method_types)
    "Nucleotide Transformer v3": ("model", "Nucleotide Transformer v3 genomic language model family (pre- and post-trained checkpoints).", ["foundation_model"]),
    "AIDO.DNA": ("model", "AIDO.DNA genomic language model.", ["foundation_model"]),
    "ESA-dna2vec": ("model", "ESA-dna2vec DNA embedding model.", ["foundation_model"]),
    "Mistral-DNA": ("model", "Mistral-architecture DNA language model.", ["foundation_model"]),
    "PhyloGPN": ("model", "Phylogenetic genomic language model (PhyloGPN).", ["foundation_model"]),
    "Enigma-Distilled": ("model", "Distilled supervised regulatory sequence model named Enigma-Distilled in GUANinE v1.1.", ["supervised_machine_learning"]),
    "hgT5": ("model", "T5 model pretrained on the human genome by the GUANinE authors (Robson and Ioannidis 2023).", ["foundation_model"]),
    "GUANinE T5 supervised baseline": ("model", "Fully supervised T5 neural baseline trained per task by the GUANinE authors.", ["supervised_machine_learning"]),
    "GC-content baseline": ("method", "Non-neural baseline using GC content of the input sequence.", ["conventional_pipeline"]),
    "5-mer LinSVR baseline": ("method", "Non-neural baseline: linear support vector regression on 5-mer counts.", ["conventional_pipeline"]),
    "5-mer kNN baseline": ("method", "Non-neural baseline: k-nearest neighbours on 5-mer counts.", ["conventional_pipeline"]),
    "ENCODE DNase track ENCFF180XQC baseline": ("method", "Non-neural baseline that reads an ENCODE DNase-seq signal file (ENCFF180XQC).", ["conventional_pipeline"]),
    "Naive VEP consequence baseline": ("method", "Non-neural baseline scoring a variant by its Ensembl VEP consequence class.", ["conventional_pipeline"]),
    "deltaSVM": ("method", "Gapped k-mer SVM variant scorer (deltaSVM).", ["supervised_machine_learning"]),
    "Sei-Aggr. scoring": ("method", "Low-dimensional aggregation of Sei outputs used as a variant score in GUANinE v1.1.", ["supervised_machine_learning"]),
    "Sei-Aggr. plus Pangolin": ("method", "Combination of the Sei-Aggr. score with the Pangolin splicing model.", ["supervised_machine_learning"]),
}

def family(label):
    l = label.replace("Naïve", "Naive")
    rules = [("NTv3", "Nucleotide Transformer v3"), ("NTv2", "Nucleotide Transformer v2"), ("Evo2", "Evo 2"),
             ("GENA-LM", "GENA-LM"), ("ChromBPNet", "ChromBPNet"), ("Caduceus", "Caduceus"), ("DNABERT-2", "DNABERT-2"),
             ("AIDO.DNA", "AIDO.DNA"), ("ESA-dna2vec", "ESA-dna2vec"), ("Mistral-DNA", "Mistral-DNA"), ("PhyloGPN", "PhyloGPN"),
             ("Enigma-Distilled", "Enigma-Distilled"), ("hgT5", "hgT5"), ("⋆ T5", "GUANinE T5 supervised baseline"),
             ("GC-content", "GC-content baseline"), ("5-mer LinSVR", "5-mer LinSVR baseline"), ("5-mer kNN", "5-mer kNN baseline"),
             ("ENCFF180XQC", "ENCODE DNase track ENCFF180XQC baseline"), ("Naive", "Naive VEP consequence baseline"),
             ("deltaSVM", "deltaSVM"), ("Sei-Aggr. + Pangolin", "Sei-Aggr. plus Pangolin"), ("Sei-Aggr.", "Sei-Aggr. scoring"),
             ("Sei", "Sei"), ("Enformer", "Enformer"), ("Borzoi", "Borzoi"), ("DeepSEA", "DeepSEA"), ("GPN-MSA", "GPN"),
             ("phyloP", "phyloP"), ("CADD", "CADD"), ("AlphaGenome", "AlphaGenome"), ("Pangolin", "Pangolin")]
    for k, f in rules:
        if k in l:
            return f
    raise KeyError(label)

fam_ids = {}
def fam_id(f):
    if f in EXISTING:
        return EXISTING[f]
    if f not in fam_ids:
        kind, desc, mt = NEW_MODELS[f]
        rid = b.rid(kind, f)
        attrs = {"reported_name": f, "entity_level": "family" if kind == "model" else "method", "source_locator": "Tables 2-4 row labels; Methods",
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
        b.entity(kind, rid, f, desc, SIDS, attrs, method_types=mt)
        fam_ids[f] = rid
    return fam_ids[f]

METHOD_TYPE = {"B": ["conventional_pipeline"], "M": ["conventional_pipeline"], "S": ["supervised_machine_learning"],
               "U": ["foundation_model"], "U + S": ["foundation_model"], "S + S": ["supervised_machine_learning"]}
REGIME = {"B": "non-neural baseline", "M": "MSA-based method", "S": "supervised pretraining", "U": "unsupervised pretraining",
          "U + S": "unsupervised and supervised pretraining", "S + S": "two supervised models combined"}
EVAL = {"F": "fine-tuned", "X": "1% eval (evaluated with 1% of the training set)", "": "zero-shot", "N": "evaluation mode not printed (Table 4 has no Eval. column)"}
EVSLUG = {"F": "ft", "X": "1pct", "": "zs", "N": "mode-unprinted"}

configs = {}
def config(label, reg, ev, ctx, table):
    key = (label, ev)
    if key in configs:
        return configs[key]
    rid = b.rid("config", label, EVSLUG[ev])
    f = family(label)
    params = f"Regime {reg} ({REGIME.get(reg, reg)}); evaluation {EVAL[ev]}; context column '{ctx}'"
    attrs = {"reported_name": label, "foundation_model_eligible": f in ("Nucleotide Transformer v3", "Nucleotide Transformer v2", "Evo 2", "Caduceus", "DNABERT-2", "GENA-LM", "AIDO.DNA", "ESA-dna2vec", "Mistral-DNA", "PhyloGPN", "hgT5", "GPN"),
             "parameters": params, "source_locator": f"{table} row '{label}', columns Reg., Eval. and Context",
             "access_reuse": "Not stated in the source; see the model's own release",
             "missing_metadata": {"version": {"reason": "unreported", "note": "Only the printed row label identifies the checkpoint"}}}
    if f in ("GPN",) and "MSA" in label:
        attrs["model_identity_note"] = "GPN-MSA, the multiple-sequence-alignment member of the GPN family"
    b.entity("configuration", rid, f"{label} ({EVAL[ev]}, GUANinE v1.1)", f"{label} as evaluated in GUANinE v1.1.", SIDS, attrs,
             method_types=METHOD_TYPE.get(reg, ["supervised_machine_learning"]), links=[{"relation": "configuration_of", "target_id": fam_id(f)}])
    configs[key] = rid
    return rid

BENCH = b.entity("benchmark", b.rid("benchmark", "guanine-v1-1"), "GUANinE v1.1",
    "Genome Understanding and ANnotation in silico Evaluation, version 1.1: functional genomics, conservation, gene-expression and variant tasks on hg38.",
    SIDS, {"entity_level": "suite", "version": "v1.1", "task": "Regulatory sequence, conservation, expression and variant-effect prediction",
           "scope_note": "Tasks in this batch: dnase-propensity, ccre-propensity, cons30, cons100, gpra-c, gpra-d (Table 2), cadd-snv (Table 3), clinvar-snv (Table 4).",
           "source_locator": "Abstract; Table 1; Tables 2-4"})

TASKS = {
    "dnase-propensity": ("DNase hypersensitivity propensity of hg38 sequences", "Table 2"),
    "ccre-propensity": ("ENCODE cCRE propensity of hg38 sequences", "Table 2"),
    "cons30": ("Sequence conservation, 30-way", "Table 2"),
    "cons100": ("Sequence conservation, 100-way", "Table 2"),
    "gpra-c": ("Yeast promoter expression (GPRA), complex library", "Table 2"),
    "gpra-d": ("Yeast promoter expression (GPRA), defined library", "Table 2"),
    "cadd-snv": ("Proxy deleteriousness of hg38 SNVs (CADD-style proxy labels; Nazaretyan et al. 2025)", "Table 3"),
    "clinvar-snv": ("ClinVar benign versus pathogenic noncoding SNVs", "Table 4"),
}
protos, datas = {}, {}
for t, (desc, table) in TASKS.items():
    d = b.entity("dataset", b.rid("data", t), f"GUANinE {t} test set", desc + ".", SIDS,
                 {"version": "GUANinE v1.1", "split": "Test set" + (" (Test22 split; Table 1)" if t in ("cadd-snv", "clinvar-snv") else ""),
                  "source_locator": "Table 1" if t in ("cadd-snv", "clinvar-snv") else "Table 2 column header",
                  **({"population": {"cadd-snv": "Test set 1.04 M SNVs (Table 1)", "clinvar-snv": "Test set 12.0 K SNVs (Table 1); predominantly benign intronic and pathogenic splice-site variants"}[t]} if t in ("cadd-snv", "clinvar-snv") else {})})
    lim = ["The benchmark authors evaluated the models; GUANinE v1.1 is by the developers of hgT5 and the T5 baseline.",
           "Previously reported performances are marked in blue in the published table; the colour is not in the XML artifact, so prior and new cells are not distinguished here.",
           "Many rows are '1% eval': models were evaluated with 1% of the training set (Table 2 footnote)."]
    if t in ("cadd-snv", "clinvar-snv"):
        lim.append("ρ against a Boolean label is a rank correlation with a binary target; the source does not define it further; not comparable with AUROC or AUPRC on similar ClinVar tasks.")
    if t == "clinvar-snv":
        lim.append("No training set; models that cannot score zero-shot were calibrated on the development set (Table 4 footnote).")
    p = b.entity("protocol", b.rid("protocol", t), f"GUANinE v1.1 {t}, Spearman rho x100 ({table})", f"GUANinE v1.1 task {t}: {desc}.", SIDS,
                 {"protocol": f"GUANinE v1.1 {t} test set; score is the printed column 'ρ'", "version": "GUANinE v1.1",
                  "metric": "spearman-correlation", "metric_direction": "higher", "unit": "unitless",
                  "unit_detail": "Printed as Spearman rho multiplied by 100",
                  "limitations": lim, "source_locator": f"{table} column '{t}'"},
                 links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": d}])
    protos[t], datas[t] = p, d

def origin_of(label):
    # hgT5, the T5 baseline, the authors' non-neural baselines and the Sei-Aggr. scoring constructions are the GUANinE authors' own.
    own = ("hgT5", "⋆ T5", "GC-content", "5-mer LinSVR", "5-mer kNN", "Sei-Aggr.")
    return "author_reported" if any(k in label for k in own) else "independent_paper"

def add_cell(table, label, reg, ev, ctx, task, printed, row_i):
    if printed in ("", "–"):
        return
    if ctx == "–":
        ctx = "dash (not applicable)"
    c = config(label, reg, ev, ctx, table)
    e = b.rid("eval", label, EVSLUG[ev], task)
    if e not in b.ids:
        b.evaluation(e, f"{label} on GUANinE {task}", SIDS, c, protos[task], datas[task], origin_of(label),
                     {"protocol_id": protos[task], "dataset_version": "GUANinE v1.1", "split": "Test set", "population": None,
                      "inputs": f"hg38 sequence; context '{ctx}'", "adaptation": EVAL[ev], "metric_implementation": "Spearman rho x100 as printed",
                      "aggregation": None, "budget": None}, f"{table} row '{label}', column '{task}'")
    loc = f"{table}, row '{label}'" + (f" with Eval. '{ev or 'blank'}'" if label == "PhyloGPN" and table == "Table 3" else "") + f", column '{task}' (ρ)"
    rid = b.rid("result", label, EVSLUG[ev], task)
    if printed == "†":
        b.result(rid, f"{label} {task}", SRC, SIDS, e, printed, "spearman-correlation", "higher", "unitless", loc, REVIEW(f"{table} body row {row_i}."),
                 qualifier="GUANinE v1.1 test set", unit_detail="Printed as Spearman rho x100",
                 value_missing={"reason": "unavailable", "note": "Printed dagger: computationally infeasible (Table 2 footnote)"})
        return
    n = num(printed)
    assert n is not None, (label, task, printed)
    b.result(rid, f"{label} {task}", SRC, SIDS, e, printed, "spearman-correlation", "higher", "unitless", loc, REVIEW(f"{table} body row {row_i}."),
             qualifier="GUANinE v1.1 test set", unit_detail="Printed as Spearman rho x100")

# Table 2
t2 = tables["Table 2"]
assert t2[2][:4] == ["Model", "Reg.", "Eval.", "Context"], t2[2]
cols = ["dnase-propensity", "ccre-propensity", "cons30", "cons100", "gpra-c", "gpra-d"]
n2 = 0
for i, row in enumerate(t2[3:], 1):
    if not row or not row[0]:
        continue
    assert len(row) == 10, row
    for task, v in zip(cols, row[4:]):
        add_cell("Table 2", row[0], row[1], row[2], row[3], task, v, i); n2 += 1
# Table 3
t3 = tables["Table 3"]
assert t3[1][:4] == ["Model", "Reg.", "Eval.", "Context"], t3[1]
for i, row in enumerate(t3[2:], 1):
    assert len(row) == 5, row
    add_cell("Table 3", row[0], row[1], row[2], row[3], "cadd-snv", row[4], i)
# Table 4 has no Eval. column
t4 = tables["Table 4"]
assert t4[1] == ["Model", "Reg.", "Context", "ρ"], t4[1]
for i, row in enumerate(t4[2:], 1):
    assert len(row) == 4, row
    # Sei-Aggr. is the authors' zero-shot construction (Table 4 footnote; Discussion), so its mode is zero-shot rather than unprinted.
    add_cell("Table 4", row[0], row[1], "" if row[0].startswith("Sei-Aggr.") else "N", row[2], "clinvar-snv", row[3], i)

# Clean empty missing_metadata on datasets
for r in b.records:
    if r["kind"] == "dataset" and not r["attributes"].get("missing_metadata"):
        r["attributes"].pop("missing_metadata", None)

counts = b.write()
print(json.dumps(counts), sum(1 for r in b.records if r["kind"] == "result"))
