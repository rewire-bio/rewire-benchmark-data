"""Wang et al. 2026, "Zero-shot benchmarking of RNA language models in structural, functional, and
evolutionary learning" (Briefings in Bioinformatics, bbag098).

Supplementary Tables 4-11 from the supplementary Word file (bbag098_supplymentary_information_20260209.docx),
read from its document.xml table cells. The main-text XML is pinned as the article source.

Usage: python3 -I extract_rnalm_zeroshot.py <fulltext.xml> <supplement.docx> <batch-folder>
"""
import sys, os, re, json, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalise, sha256, slug, num

xml_path, docx_path, folder = sys.argv[1], sys.argv[2], sys.argv[3]
SHA = sha256(xml_path)
SHA_S = sha256(docx_path)
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12963973/fullTextXML"
URL_S = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12963973/supplementaryFiles"
assert SHA == "835b64d52ae892cad113e798b2976c398dc9ed12178f675e0eabd2169f533808", SHA
assert SHA_S == "c8fc78c3d8538c9431fc0448a4068a7643dfb7d74558877fd40b36feba71e214", SHA_S

P = "lit-rna-20261011-rnalm-zeroshot"
b = Batch(folder, P)
SRC = b.source(P + "-source-wang2026", "Zero-shot benchmarking of RNA language models in structural, functional, and evolutionary learning", {
    "url": "https://doi.org/10.1093/bib/bbag098", "artifact_url": URL,
    "version": "Briefings in Bioinformatics 2026, bbag098 (issue date 2026-03-01); PMC12963973 full-text XML",
    "retrieved_at": "2026-10-11T21:27:04Z", "artifact_sha256": SHA, "doi": "10.1093/bib/bbag098",
    "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml",
    "limitations": ["All benchmark numbers are in the supplementary Word file; the main text shows them as figures only."]})
SRC_S = b.source(P + "-source-wang2026-supplement", "Zero-shot benchmarking of RNA language models: Supplementary Information", {
    "url": "https://doi.org/10.1093/bib/bbag098", "artifact_url": URL_S,
    "version": "bbag098_supplymentary_information_20260209.docx from the Europe PMC supplementary files archive for PMC12963973",
    "retrieved_at": "2026-10-11T21:27:04Z", "artifact_sha256": SHA_S, "doi": "10.1093/bib/bbag098",
    "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
    "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "limitations": ["The upward arrows in the column headers are in a symbol font and are lost in the text runs; directions are taken from the Methods.",
                    "Bold marks (best per model class) are not recorded."]})
SIDS = [SRC_S, SRC]

def review(loc):
    return extraction_review(["deterministic-table-parse"],
        "Parsed the table cells (w:tc runs) of word/document.xml in the pinned supplementary .docx with extract/extract_rnalm_zeroshot.py; row label and column header taken from the same table. " + loc, SHA_S, URL_S)

# --- parse the docx tables, keyed by the caption paragraph that precedes each table
x = zipfile.ZipFile(docx_path).read("word/document.xml").decode("utf8")
body = x[x.index("<w:body>"):]
txt = lambda s: "".join(re.findall(r"<w:t(?: [^>]*)?>([^<]*)</w:t>", s))
tables, caption = {}, None
for part in re.findall(r"(<w:p[ >].*?</w:p>|<w:tbl>.*?</w:tbl>)", body, re.S):
    if part.startswith("<w:tbl>"):
        rows = [[txt(c).strip() for c in re.findall(r"<w:tc>.*?</w:tc>", r, re.S)] for r in re.findall(r"<w:tr[ >].*?</w:tr>", part, re.S)]
        m = re.match(r"Supplementary Table (\d+)\.", caption or "")
        if m:
            tables[int(m.group(1))] = (caption, rows)
        caption = None
    else:
        t = txt(part).strip()
        if t:
            caption = t
assert sorted(tables) == list(range(1, 12)), sorted(tables)

# --- model identities
EXISTING = {"RNA-FM": "discovery-model-rna-fm", "RNA-MSM": "gfm2-20261011-you2026-model-rna-msm", "RNABERT": "gfm2-20261011-you2026-model-rnabert",
            "RNAErnie": "gfm2-20261011-you2026-model-rnaernie", "SpliceBERT": "gfm2-20261011-you2026-model-splicebert",
            "UTR_LM": "gfm2-20261011-you2026-model-utr-lm", "DNABERT": "gfm2-20261011-you2026-model-dnabert",
            "DNABERT-2": "discovery-model-dnabert-2", "NT": "catalog-model-nt-v2", "LucaOne": "lit-genomics-20261011-geneb-model-lucaone",
            "EVO1": "lit-genomics-20261011-geneb-model-evo", "EVO1.5": "lit-genomics-20261011-geneb-model-evo"}
NEW = {"3UTRBERT": "3UTRBERT, a BERT language model pretrained on 3' UTR sequences.",
       "AIDO.RNA": "AIDO.RNA RNA foundation model (650M and 1.6B parameter checkpoints).",
       "BiRNA-BERT": "BiRNA-BERT RNA language model with adaptive nucleotide and BPE tokenisation.",
       "DGRNA": "DGRNA long-context RNA foundation model with bidirectional Mamba2 attention.",
       "ERNIE-RNA": "ERNIE-RNA RNA language model with structure-enhanced representations.",
       "GenerRNA": "GenerRNA autoregressive generative RNA language model.",
       "LAMAR": "LAMAR RNA foundation model pretrained on mammalian genome and transcriptome sequences (2k and 4k context checkpoints).",
       "MP-RNA": "MP-RNA RNA language model.",
       "PlantRNA-FM": "PlantRNA-FM RNA foundation model pretrained on plant transcriptomes.",
       "ProtRNA": "ProtRNA RNA language model adapted from a protein language model.",
       "RFamLlama": "RFamLlama autoregressive RNA language model trained on Rfam families (base and large).",
       "RiNALMo": "RiNALMo RNA language model (micro, mega and giga checkpoints).",
       "RNA-km": "RNA-km RNA language model.",
       "Uni-RNA": "Uni-RNA RNA foundation model (L8, L12 and L16 checkpoints)."}
DNA = ("DNABERT", "DNABERT-2", "NT", "EVO1", "EVO1.5")
# Supplementary Table 1 versions and download dates (row label -> (URL, download date, version text)).
s1 = {r[0].strip(): r[1:] for r in tables[1][1][1:] if len(r) == 4 and r[1].strip()}

fam = {}
def family(name):
    if name in EXISTING:
        return EXISTING[name]
    if name not in fam:
        rid = b.rid("model", name)
        b.entity("model", rid, name, NEW[name], [SRC_S],
                 {"reported_name": name, "entity_level": "family", "source_locator": f"Supplementary Table 1 row '{name}'",
                  "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the checkpoint is on the configuration"}}},
                 method_types=["foundation_model"])
        fam[name] = rid
    return fam[name]

def split_label(label):
    star = label.startswith("*")
    m = re.match(r"^\*?(.+?)(?: \((.+)\))?$", label.strip())
    return m.group(1).strip(), (m.group(2) or "").strip(), star

cfgs = {}
def config(name, variant):
    key = (name, variant)
    if key in cfgs:
        return cfgs[key]
    rid = b.rid("config", name, variant, "wang2026")
    row = s1.get(name)
    shown = f"{name} ({variant})" if variant else name
    attrs = {"reported_name": shown, "foundation_model_eligible": True,
             "parameters": "Pretrained weights used without fine-tuning (zero-shot); attention maps, embeddings or token logits read out as described in the Methods",
             "access_reuse": "Public download location listed in Supplementary Table 1" if row else "Not stated in the source",
             "source_locator": f"Supplementary Table 1 row '{name}'" if row else "Supplementary Tables 4-11 row labels"}
    if row:
        attrs["checkpoint"] = f"{row[0].strip()} (downloaded {row[1].strip()}; version column '{row[2].strip()}'; variant label in results tables '{variant or 'none'}')"
        attrs["version"] = variant or row[2].strip()
        if attrs["version"] in ("-", ""):
            del attrs["version"]
    if "version" not in attrs:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "No version column entry for this checkpoint in Supplementary Table 1"}}
    b.entity("configuration", rid, f"{shown} (zero-shot, Wang et al. 2026)",
             f"{shown} evaluated zero-shot by Wang et al. 2026.", [SRC_S], attrs, method_types=["foundation_model"],
             links=[{"relation": "configuration_of", "target_id": family(name)}])
    cfgs[key] = rid
    return rid

BENCH = b.entity("benchmark", b.rid("benchmark", "wang2026-zero-shot-rna-lm"), "Zero-shot RNA language model benchmark (Wang et al. 2026)",
    "Standardised zero-shot evaluation of 21 RNA language models, with DNA language models as reference controls, on attention-based secondary structure prediction, embedding-based RNA classification and likelihood-based mutational fitness prediction.",
    SIDS, {"entity_level": "suite", "version": "Published 2026", "task": "Zero-shot RNA secondary structure, RNA classification and ncRNA fitness prediction",
           "scope_note": "No fine-tuning. Secondary structure on TS (70 PDB structures) and TS-Hard (15) with a head-layer and threshold chosen on VL1 (40); classification of homologous versus non-homologous sequence pairs on RfamSample (561 Rfam families) and ArchiveII-Nr (1273 RNAs) from FFT or CLS embeddings; fitness on 31 RNAGym ncRNA deep mutational scanning assays (wild-type length <= 440 nt) with WT-LLR or PLL-D scores.",
           "source_locator": "Main text Methods 'RNA secondary structure', 'RNA classification', 'RNA DMS assays'; Supplementary Tables 4-11",
           "limitations": ["RNA-MSM is from the corresponding authors' group (Zhang et al.); the TS and VL1 sets come from the same group's earlier work (ref. 29).",
                           "Models are included per task only where their attention, embeddings or logits were available (Supplementary Table 3)."]})

DATA = {
    "ts": ("TS test set (70 PDB structures)", "Independent test set of 70 PDB RNA structures with base pairs from 3D structures; sequence identity < 80% and TM-score < 0.45 to the VL1 validation set.", "Test (TS)"),
    "ts-hard": ("TS-Hard test set (15 PDB structures)", "Subset of TS with no Rfam family shared with VL1 (Infernal homology detection).", "Test (TS-Hard)"),
    "rfamsample": ("RfamSample (561 Rfam families)", "10 sequences (length <= 1024, < 80% identity within family) from each Rfam 14.0 seed family with more than 10 members; 100,000 homologous and 100,000 non-homologous pairs sampled.", "Whole dataset (zero-shot)"),
    "archiveii-nr": ("ArchiveII-Nr (1273 RNAs)", "ArchiveII without long group II introns, made non-redundant at 80% identity with MMseqs2; homology defined at the RNA type level.", "Whole dataset (zero-shot)"),
    "rnagym-ncrna31": ("RNAGym ncRNA DMS assays (31 assays)", "31 ncRNA deep mutational scanning assays from RNAGym with wild-type length <= 440 nt.", "Whole dataset (zero-shot)"),
}
data_ids = {k: b.entity("dataset", b.rid("data", k), f"{v[0]} (Wang et al. 2026)", v[1], [SRC],
                        {"version": "As constructed by Wang et al. 2026 (Zenodo record 18218776)", "split": v[2],
                         # Review C3: only ArchiveII-Nr is described in Supplementary Table 2.
                         "source_locator": "Main text Methods 'Datasets'; Supplementary Table 2 for ArchiveII" if k == "archiveii-nr" else "Main text Methods 'Datasets'"}) for k, v in DATA.items()}

# table -> (data key, task phrase, representation or score, adaptation text)
TABLES = {
    4: ("ts", "secondary structure", "attention", "Zero-shot: symmetrised, APC-corrected attention map from one head-layer and threshold chosen on VL1 by F1"),
    5: ("ts-hard", "secondary structure", "attention", "Zero-shot: symmetrised, APC-corrected attention map from one head-layer and threshold chosen on VL1 by F1"),
    6: ("rfamsample", "family classification", "FFT embedding", "Zero-shot: cosine similarity of FFT-reduced last-hidden-state embeddings"),
    7: ("archiveii-nr", "RNA type classification", "FFT embedding", "Zero-shot: cosine similarity of FFT-reduced last-hidden-state embeddings"),
    8: ("rfamsample", "family classification", "CLS embedding", "Zero-shot: cosine similarity of CLS-token embeddings"),
    9: ("archiveii-nr", "RNA type classification", "CLS embedding", "Zero-shot: cosine similarity of CLS-token embeddings"),
    10: ("rnagym-ncrna31", "fitness", "WT-LLR", "Zero-shot: wild-type conditioned log-likelihood ratio from token logits"),
    11: ("rnagym-ncrna31", "fitness", "PLL-D", "Zero-shot: pseudo-log-likelihood difference from token logits"),
}
METRIC = {"F1": ("f1-score", "higher"), "F1 score": ("f1-score", "higher"), "MCC": ("matthews-correlation-coefficient", "higher"),
          "AUC": ("auroc", "higher"), "1 − OR": ("one-minus-overlap-ratio", "higher"), "SR": ("absolute-spearman-correlation", "higher")}
UNITS = {"ts": "structures", "ts-hard": "structures", "rnagym-ncrna31": "assays"}

protos = {}
def protocol(t, col, agg):
    key = (t, col, agg)
    if key in protos:
        return protos[key]
    dk, task, rep, adapt = TABLES[t]
    metric, direction = METRIC[col]
    aggtext = {"median": f"median over {UNITS.get(dk, 'items')}", "mean": f"mean over {UNITS.get(dk, 'items')}",
               "sampled-mean": "mean over repeated random samplings of sequence pairs"}[agg]
    name = f"Wang et al. 2026 zero-shot {task}, {DATA[dk][0]}, {rep}, {col} ({aggtext})"
    pid = b.entity("protocol", b.rid("protocol", f"t{t}", col, agg), name,
                   f"{adapt}; {col} reported as {aggtext} (Supplementary Table {t}).", SIDS,
                   {"protocol": f"{adapt}. Metric {col}, {aggtext}.", "version": "Wang et al. 2026",
                    "metric": metric, "metric_direction": direction, "unit": "unitless",
                    "metric_qualifier": f"{rep}; {aggtext}",
                    "source_locator": f"Supplementary Table {t} caption and column '{col}'; main text Methods",
                    "limitations": ["Zero-shot only; no fine-tuning or task head.",
                                    "Binarisation for MCC, F1 and AUC in the fitness task is not described in the main text or supplement." if dk == "rnagym-ncrna31" else
                                    ("Classification metrics are computed on cosine similarities of sampled homologous versus non-homologous pairs; the threshold used for F1 and MCC is not stated." if task.endswith("classification") else
                                     "Base pairs come from 3D structures; one head-layer and threshold per model chosen on VL1.")]},
                   links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": data_ids[dk]}])
    if t in (6, 7, 8, 9) and col == "F1":  # review C4
        b.records[-1]["attributes"]["limitations"].append(
            "Many rows print F1 0.667 with MCC near 0, which is what a classifier that labels every pair homologous scores when the two classes are equal in size; the source does not describe the decision threshold for F1 and MCC.")
    protos[key] = pid
    return pid

def add(t, label, col, agg, printed, row_i):
    name, variant, star = split_label(label)
    assert name in EXISTING or name in NEW, label
    dk, task, rep, adapt = TABLES[t]
    c = config(name, variant)
    p = protocol(t, col, agg)
    vslug = variant or "default"
    e = b.rid("eval", name, vslug, f"t{t}", col, agg)
    excl = None
    if star and t in (7, 9):  # review C2: the Table 7 and 9 notes give 440 nt only
        excl = "Starred row: sequences longer than 440 nt were excluded (table note)"
    elif star:
        excl = "Starred row: sequences longer than the model's limit (440 or 512 nt) were excluded" + (" (69 of 70 TS structures)" if t == 4 else " (14 of 15 TS-Hard structures)" if t == 5 else "")
    origin = "author_reported" if name == "RNA-MSM" else "independent_paper"
    b.evaluation(e, f"{label.lstrip('*')} zero-shot {task} on {DATA[dk][0]} ({rep}, {col}, {agg})", SIDS, c, p, data_ids[dk], origin,
                 {"protocol_id": p, "dataset_version": "Wang et al. 2026", "split": DATA[dk][2],
                  "population": excl, "inputs": rep, "adaptation": adapt, "metric_implementation": col,
                  "aggregation": {"median": "Median", "mean": "Mean", "sampled-mean": "Mean over random samplings"}[agg], "budget": None},
                 f"Supplementary Table {t}, row '{label}'")
    metric, direction = METRIC[col]
    aggtext = {"median": f"median over {UNITS.get(dk, 'items')}", "mean": f"mean over {UNITS.get(dk, 'items')}",
               "sampled-mean": "mean over random samplings of sequence pairs"}[agg]
    unc = None
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)±(\d+(?:\.\d+)?)", printed)
    if m:
        unc = {"type": "standard_deviation", "value": m.group(2), "center": m.group(1), "printed": printed,
               "scope": {"median": "", "mean": f"across {UNITS.get(dk, 'items')}", "sampled-mean": "across random samplings of sequence pairs"}[agg]}
        if not unc["scope"]:
            del unc["scope"]
        numeric = m.group(1)
    else:
        assert agg == "median", (t, label, col, printed)
        numeric = num(printed)
        assert numeric is not None, (t, label, col, printed)
    loc = f"Supplementary Table {t}, row '{label}', column '{col}'" + {"median": " (Median)", "mean": " (Mean ± Std)", "sampled-mean": ""}[agg]
    b.result(b.rid("result", name, vslug, f"t{t}", col, agg), f"{label.lstrip('*')} {task} {DATA[dk][0]} {rep} {col} {agg}", SRC_S, SIDS, e,
             printed, metric, direction, "unitless", loc, review(f"Supplementary Table {t} body row {row_i}."),
             qualifier=f"{rep}; {aggtext}", uncertainty=unc, numeric=numeric)

counts_by_table = {}
for t in range(4, 12):
    cap, rows = tables[t]
    hdr = rows[0]
    if t in (4, 5):
        assert hdr == ["Model", "F1 score", "MCC"], hdr
        assert rows[1][1:] == ["Median", "Mean  Std", "Median ()", "Mean  Std"], rows[1]
        cols = [("F1 score", "median"), ("F1 score", "mean"), ("MCC", "median"), ("MCC", "mean")]
        data_rows = rows[2:]
    elif t in (6, 7, 8, 9):
        assert hdr == ["Model", "F1", "MCC", "AUC", "1 − OR ()"], hdr
        cols = [("F1", "sampled-mean"), ("MCC", "sampled-mean"), ("AUC", "sampled-mean"), ("1 − OR", "sampled-mean")]
        data_rows = rows[1:]
    else:
        assert hdr == ["Model", "MCC", "AUC", "SR"], hdr
        assert rows[1][1:] == ["Median", "Mean  Std", "Median", "Mean  Std", "Median ()", "Mean  Std"], rows[1]
        cols = [("MCC", "median"), ("MCC", "mean"), ("AUC", "median"), ("AUC", "mean"), ("SR", "median"), ("SR", "mean")]
        data_rows = rows[2:]
    n = 0
    for i, r in enumerate(data_rows, 1):
        if r[0] in ("DNA LMs", "Class I RNA LMs", "Class II RNA LMs", "Class III RNA LMs"):
            assert all(v == "" for v in r[1:]), r
            continue
        assert len(r) == len(cols) + 1, (t, r)
        for (col, agg), v in zip(cols, r[1:]):
            add(t, r[0], col, agg, v.strip(), i)
            n += 1
    counts_by_table[t] = n

# Review C1: RFamLlama prints 1 - OR 0.000±0.000 next to an AUC well above 0.5.
C1_AUC = {("base", 6): "0.660±0.001", ("large", 6): "0.685±0.001", ("base", 7): "0.613±0.001", ("large", 7): "0.654±0.002",
          ("base", 8): "0.654±0.001", ("large", 8): "0.688±0.002", ("base", 9): "0.613±0.002", ("large", 9): "0.655±0.001"}
recs = {r["id"]: r for r in b.records}
disputed = {}
for (size, t), auc in C1_AUC.items():
    rid = f"{P}-result-rfamllama-{size}-t{t}-1-or-sampled-mean"
    assert recs[rid]["attributes"]["printed_value"] == "0.000±0.000", rid
    assert recs[f"{P}-result-rfamllama-{size}-t{t}-auc-sampled-mean"]["attributes"]["printed_value"] == auc, (rid, auc)
    disputed[rid] = [f"Supplementary Table {t} prints 1 − OR 0.000±0.000 for this row, meaning the homologous and non-homologous similarity distributions overlap completely, but prints AUC {auc} in the same row; complete overlap implies an AUC near 0.5. Recorded as printed; not resolved from the source."]
finalise(b.records, "reviewer-ro-1",
         "Re-fetched the Europe PMC supplementary archive; the .docx inside matched its SHA-256. An independent w:tc parse of Supplementary Tables 4-11 matched all 1190 printed values, numeric values, standard deviations and locators; 48 cells were also checked by hand against a textutil rendering.",
         disputed=disputed)

counts = b.write()
print(json.dumps(counts), json.dumps(counts_by_table))
