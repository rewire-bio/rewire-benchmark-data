"""ViroBench (Ye et al., arXiv 2605.25388v1, KDD 2026): Table 25 and the two Table 4 rows absent from it.

Table 25 is the appendix Macro-F1 table for viral taxonomy and host classification over the full suite.
Table 4 is the main-text subset; its rows are checked against Table 25 and only the rows that Table 25
does not print (ViroDNABERT2, ViroCaduceus) are added from Table 4.

Usage: python3 -I extract_virobench.py <arxiv-pdf> <pdftotext -layout output> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, reviewed_review, source_review, mark_reviewed, sha256, slug, num

pdf_path, txt_path, folder = sys.argv[1], sys.argv[2], sys.argv[3]
SHA = sha256(pdf_path)
TXT_SHA = sha256(txt_path)
URL = "https://arxiv.org/pdf/2605.25388v1"
assert SHA == "22ad7d742eeba37dd7f7f407a483776ba15fc38dedfb8c27ec05f5db231f9e42", SHA

P = "lit-microbial-20261011-virobench"
b = Batch(folder, P, areas=["microbes-communities", "dna-genomes"])
SRC = b.source(P + "-source-ye2026", "ViroBench: Benchmarking Nucleotide Foundation Models on Viral Genomics Tasks", {
    "url": "https://arxiv.org/abs/2605.25388v1", "artifact_url": URL,
    "version": "arXiv 2605.25388v1 (submitted 2026-05-25); 42-page PDF; KDD '26 header on every page",
    "retrieved_at": "2026-10-11T21:24:29Z", "artifact_sha256": SHA, "doi": "10.48550/arXiv.2605.25388",
    "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "application/pdf",
    "code_url": "https://github.com/QIANJINYDX/ViroBench",
    "limitations": [
        "The pages carry a KDD '26 conference header and the arXiv page lists a related ACM DOI (10.1145/3770855.3819057); the conference version was not retrieved, so the record stays at the arXiv preprint.",
        "Values were read from the pdftotext (poppler 26.08.0) layout text layer of the PDF; the archived copy is that text layer, SHA-256 " + TXT_SHA + ".",
        "Table 3 lists NT v3 under phage-specific coverage (P) and Table 9 lists it as non-viral (N); Table 25 groups NTv3 rows under phage-specific coverage.",
    ]})
SIDS = [SRC]
REVIEW = lambda loc: extraction_review(["pdf-text-parse"],
    "Parsed the pdftotext -layout text layer of the pinned arXiv PDF with extract/extract_virobench.py; each row has a label and twelve 'mean (sd)' cells asserted. " + loc,
    SHA, URL)

lines = open(txt_path, encoding="utf-8").read().split("\n")

# Existing store records for model families.
EXISTING = {
    "BLAST": "dna-pathogen-20261009-method-blast", "Kraken2": "catalog-model-kraken2",
    "DNABERT-S": "lit-genomics-20261011-geneb-model-dnabert-s", "GenomeOcean": "lit-genomics-20261011-geneb-model-genomeocean",
    "LucaOne": "lit-genomics-20261011-geneb-model-lucaone", "Evo": "lit-genomics-20261011-geneb-model-evo",
    "Evo 2": "discovery-model-evo-2", "Nucleotide Transformer v3": "lit-genomics-20261011-guanine-model-nucleotide-transformer-v3",
    "Nucleotide Transformer": "discovery-model-nucleotide-transformer", "Nucleotide Transformer v2": "catalog-model-nt-v2",
    "AIDO.DNA": "lit-genomics-20261011-guanine-model-aido-dna", "Caduceus": "regulatory-variant-20261009-model-caduceus",
    "HyenaDNA": "regulatory-variant-20261009-model-hyenadna", "DNABERT-2": "discovery-model-dnabert-2",
    "DNABERT": "lit-genomics-20261011-gfmbench-model-dnabert", "GENA-LM": "regulatory-variant-20261009-model-gena-lm",
    "GROVER": "lit-genomics-20261011-geneb-model-grover", "GENERator": "lit-genomics-20261011-geneb-model-generator",
    "RNA-FM": "discovery-model-rna-fm", "RNABERT": "gfm2-20261011-you2026-model-rnabert",
}
NEW = {  # family -> (kind, description, method_types)
    "LucaVirus": ("model", "LucaVirus unified nucleotide-protein language model for viruses.", ["foundation_model"]),
    "Genos": ("model", "Genos genomic foundation model family (mixture-of-experts transformer; ViroBench Table 9).", ["foundation_model"]),
    "OmniReg-GPT": ("model", "OmniReg-GPT generative genomic foundation model.", ["foundation_model"]),
    "AIDO.RNA": ("model", "AIDO.RNA RNA language model family.", ["foundation_model"]),
    "RiNALMo": ("model", "RiNALMo RNA language model.", ["foundation_model"]),
    "BiRNA-BERT": ("model", "BiRNA-BERT RNA language model.", ["foundation_model"]),
    "MP-RNA": ("model", "MP-RNA RNA language model.", ["foundation_model"]),
    "ViroHyena": ("model", "Hyena-architecture nucleotide model pretrained on viral sequences by the ViroBench authors (in-house model).", ["foundation_model"]),
    "ViroDNABERT2": ("model", "DNABERT-2-architecture model pretrained on viral sequences by the ViroBench authors (in-house model).", ["foundation_model"]),
    "ViroCaduceus": ("model", "Caduceus-architecture model pretrained on viral sequences by the ViroBench authors (in-house model).", ["foundation_model"]),
    "ViroBench BiLSTM baseline": ("method", "Bidirectional LSTM trained from scratch as a non-foundation baseline in ViroBench.", ["supervised_machine_learning"]),
    "ViroBench CNN baseline": ("method", "Residual 1D CNN trained from scratch as the non-pretrained baseline in ViroBench (Appendix Figure 4).", ["supervised_machine_learning"]),
}
RULES = [("BLAST", "BLAST"), ("Kraken2", "Kraken2"), ("BiLSTM", "ViroBench BiLSTM baseline"), ("CNN", "ViroBench CNN baseline"),
         ("LucaOne", "LucaOne"), ("LucaVirus", "LucaVirus"), ("DNABERT-S", "DNABERT-S"), ("GenomeOcean", "GenomeOcean"),
         ("Evo2", "Evo 2"), ("Evo1", "Evo"), ("NTv3", "Nucleotide Transformer v3"), ("NTv2", "Nucleotide Transformer v2"),
         ("NT-", "Nucleotide Transformer"), ("AIDO.DNA", "AIDO.DNA"), ("AIDO.RNA", "AIDO.RNA"), ("Caduceus", "Caduceus"),
         ("Genos", "Genos"), ("HyenaDNA", "HyenaDNA"), ("DNABERT-2", "DNABERT-2"), ("DNABERT-", "DNABERT"), ("GENA-LM", "GENA-LM"),
         ("GROVER", "GROVER"), ("OmniReg-GPT", "OmniReg-GPT"), ("GENERator", "GENERator"), ("RNA-FM", "RNA-FM"),
         ("RiNALMo", "RiNALMo"), ("BiRNA-BERT", "BiRNA-BERT"), ("RNABERT", "RNABERT"), ("MP-RNA", "MP-RNA"),
         ("ViroHyena", "ViroHyena"), ("ViroDNABERT2", "ViroDNABERT2"), ("ViroCaduceus", "ViroCaduceus")]
# ViroCaduceus must not match the Caduceus rule first.
RULES = [r for r in RULES if r[0].startswith("Viro")] + [r for r in RULES if not r[0].startswith("Viro")]

def family(label):
    for k, f in RULES:
        if label.startswith(k) or (k in ("NT-",) and label.startswith(k)):
            return f
    raise KeyError(label)

fam_ids = {}
def fam_id(f):
    if f in EXISTING:
        return EXISTING[f]
    if f not in fam_ids:
        kind, desc, mt = NEW[f]
        rid = b.rid(kind, f)
        attrs = {"reported_name": f, "entity_level": "family" if kind == "model" else "method",
                 "source_locator": "Table 3; Table 9; Table 25 row labels",
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
        b.entity(kind, rid, f, desc, SIDS, attrs, method_types=mt)
        fam_ids[f] = rid
    return fam_ids[f]

SECTION_LINEAGE = {
    "Baseline": ("baseline", None),
    "DNA Foundation Models (Diverse Viral Coverage)": ("DNA foundation model", "diverse viral coverage"),
    "DNA Foundation Models (Phage-specific Coverage)": ("DNA foundation model", "phage-specific coverage"),
    "DNA Foundation Models (Non-viral Coverage)": ("DNA foundation model", "non-viral coverage"),
    "RNA Foundation Models (RNA-specific Coverage)": ("RNA foundation model", "RNA-specific coverage"),
    "RNA Foundation Models (Non-viral Coverage)": ("RNA foundation model", "non-viral coverage"),
    "In-house Models": ("in-house model", None),
}
IN_HOUSE = ("ViroHyena", "ViroDNABERT2", "ViroCaduceus", "ViroBench BiLSTM baseline", "ViroBench CNN baseline")

def method_types(f, section):
    if f in ("BLAST", "Kraken2"):
        return ["conventional_pipeline"]
    if f in ("ViroBench BiLSTM baseline", "ViroBench CNN baseline"):
        return ["supervised_machine_learning"]
    return ["foundation_model"]

configs = {}
def config(label, section, table):
    if label in configs:
        return configs[label]
    f = family(label)
    rid = b.rid("config", label)
    kind_label, lineage = SECTION_LINEAGE[section]
    if f in ("BLAST", "Kraken2"):
        params = "Similarity-search baseline run by the ViroBench authors; reference database not stated in the table"
    elif f in ("ViroBench BiLSTM baseline", "ViroBench CNN baseline"):
        params = "Trained from scratch on the ViroBench training split (non-pretrained baseline)"
    else:
        params = ("Frozen backbone; sequence embeddings from windows of 512, 1024 or 2048 bp fed to a standardised MLP head "
                  "(Section 4.1.2; Appendix B.3)") + (f"; pretraining coverage lineage: {lineage}" if lineage else "")
    attrs = {"reported_name": label, "foundation_model_eligible": method_types(f, section) == ["foundation_model"],
             "parameters": params, "source_locator": f"{table} row '{label}' (section '{section}'); Table 9",
             "access_reuse": "Not stated in the source; see the model's own release",
             "missing_metadata": {"version": {"reason": "unreported", "note": "The printed row label is the only checkpoint identifier; Table 9 lists evaluated sub-modes"}}}
    name = f"{label} (ViroBench classification)"
    b.entity("configuration", rid, name, f"{label} as evaluated in ViroBench viral taxonomy and host classification.", SIDS, attrs,
             method_types=method_types(f, section), links=[{"relation": "configuration_of", "target_id": fam_id(f)}])
    configs[label] = rid
    return rid

BENCH = b.entity("benchmark", b.rid("benchmark", "virobench"), "ViroBench",
    "Benchmark of nucleotide foundation models on viral genomics: taxonomy and host classification under genus-disjoint and temporal splits, plus genome modelling and CDS generation.",
    SIDS, {"entity_level": "suite", "version": "arXiv 2605.25388v1", "task": "Viral taxonomy and host classification; viral genome modelling and CDS generation",
           "scope_note": "This batch covers the classification axis only (Table 25 and two Table 4 rows): 12 protocols, ALL, DNA and RNA virus sets x taxonomy and host x genus-disjoint and temporal splits. Generation results (Tables 5, 6, 27, 28) are not extracted.",
           "source_locator": "Abstract; Section 3; Table 1; Table 25"})

SETS = {"ALL": "ALL viruses", "DNA": "DNA viruses", "RNA": "RNA viruses"}
SPLITS = {"G": ("G-Split", "genus-disjoint split, 8:1:1 train/validation/test"), "T": ("T-Split", "temporal split by collection date")}
SPLIT_DETAIL = {("ALL", "T"): "validation and test cutoffs 2017.10 and 2020.02", ("DNA", "T"): "validation and test cutoffs 2022.07 and 2023.08",
                ("RNA", "T"): "validation and test cutoffs 2017.03 and 2017.11"}
TASKS = {"Taxonomy": "taxonomy classification", "Host": "host classification"}
COLS = [(s, t, sp) for s in ("ALL", "DNA", "RNA") for t in ("Taxonomy", "Host") for sp in ("G", "T")]

datas, protos = {}, {}
for s in SETS:
    for sp, (sp_label, sp_desc) in SPLITS.items():
        detail = SPLIT_DETAIL.get((s, sp), "")
        datas[(s, sp)] = b.entity("dataset", b.rid("data", s, sp_label), f"ViroBench {SETS[s]}, {sp_label} test set",
            f"ViroBench {SETS[s]} classification set, {sp_desc}" + (f" ({detail})" if detail else "") + ".", SIDS,
            {"version": "ViroBench (arXiv 2605.25388v1)", "split": f"{sp_label} test partition" + (f"; {detail}" if detail else ""),
             "source_locator": "Table 1, Panel " + {"ALL": "A", "DNA": "B", "RNA": "C"}[s]})
for (s, t, sp) in COLS:
    sp_label = SPLITS[sp][0]
    lim = ["The benchmark authors ran every model, including their own in-house ViroHyena, ViroDNABERT2 and ViroCaduceus models and the BiLSTM and CNN baselines.",
           "Results are the mean (standard deviation) across hyperparameter settings (window sizes 512, 1024 and 2048 with 8, 4 and 2 sampled windows, and learning rates 1e-2 to 1e-4), not across random seeds (Section 4.1.2).",
           "Values are printed without a unit; the ablation tables state Macro-F1 in %, so they are recorded as percent."]
    if t == "Taxonomy":
        lim.append("The taxonomy column is a single Macro-F1 per model; the source predicts five ranks (Kingdom to Family) and does not state how they are combined. For the rows checked, the value equals the mean of the five per-rank values in Table 26; this is an observation, not a stated aggregation.")
    protos[(s, t, sp)] = b.entity("protocol", b.rid("protocol", s, t, sp_label), f"ViroBench {SETS[s]} {TASKS[t]}, {sp_label}, Macro-F1",
        f"ViroBench {TASKS[t]} on {SETS[s]} under the {SPLITS[sp][1]}; frozen embeddings with a standardised MLP head, window-level predictions aggregated to sequence level.", SIDS,
        {"protocol": f"ViroBench classification, {SETS[s]}, {t}, {sp_label}; score is Macro-F1 as printed in Table 25",
         "version": "arXiv 2605.25388v1", "metric": "macro-f1", "metric_direction": "higher", "unit": "percent",
         "unit_detail": "Macro-F1 x100 as printed", "limitations": lim,
         "source_locator": f"Table 25, column group '{SETS[s]}', '{t}', '{sp_label}'"},
        links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[(s, sp)]}])

CELL = re.compile(r"(-?\d+\.\d+)\s*\((\d+\.\d+)\)")

def parse_rows(start, stop):
    rows, section = [], None
    for i in range(start, stop):
        ln = lines[i].strip()
        if ln in SECTION_LINEAGE:
            section = ln
            continue
        cells = CELL.findall(ln)
        if not cells:
            continue
        label = CELL.split(ln)[0].strip()
        assert len(cells) == 12, (i, ln)
        assert section, (i, ln)
        rows.append((i + 1, label, section, cells))
    return rows

def find(prefix, after=0):
    for i in range(after, len(lines)):
        if lines[i].strip().startswith(prefix):
            return i
    raise ValueError(prefix)

t25a = find("Table 25: Macro-F1 scores for viral taxonomy and host classification. Evaluation covers")
t25b = find("Table 25: Macro-F1 scores for viral taxonomy and host classification (continued).", t25a)
t26 = find("Table 26: Macro-F1 scores on the ALL-Taxon task", t25b)
end_a = next(i for i in range(t25a, t25b) if "KDD ’26" in lines[i])
rows25 = parse_rows(t25a, end_a) + parse_rows(t25b, t26)
labels25 = [r[1] for r in rows25]
assert len(rows25) == 74, len(rows25)  # 66 NFMs, 4 baselines and 4 in-house ViroHyena checkpoints
assert len(set(labels25)) == len(labels25)

t4 = find("Table 4: Macro-F1 scores for viral taxonomy and host classification.")
t4_end = find("close sequence matches in the reference database.", t4)
rows4 = parse_rows(t4, t4_end)
assert len(rows4) == 34, len(rows4)

# Table 4 rows that also appear in Table 25 must agree cell by cell (labels differ only in case).
by25 = {l.lower(): c for (_, l, _, c) in rows25}
alias = {"evo1-131k": "evo1-131k-base", "evo1.5-8k": "evo1.5-8k-base", "generator-v2-prokaryote-3b": "generator-v2-prokaryote-3b-base"}
extra4 = []
for (ln, label, section, cells) in rows4:
    key = alias.get(label.lower(), label.lower())
    if key in by25:
        assert by25[key] == cells, (label, cells, by25[key])
    else:
        extra4.append((ln, label, section, cells))
assert [r[1] for r in extra4] == ["ViroDNABERT2", "ViroCaduceus"], extra4

def origin_of(label):
    return "author_reported" if family(label) in IN_HOUSE else "independent_paper"

def add_row(table, ln, label, section, cells):
    c = config(label, section, table)
    for (s, t, sp), (mean, sd) in zip(COLS, cells):
        sp_label = SPLITS[sp][0]
        e = b.rid("eval", label, s, t, sp_label)
        b.evaluation(e, f"{label} on ViroBench {SETS[s]} {TASKS[t]} ({sp_label})", SIDS, c, protos[(s, t, sp)], datas[(s, sp)], origin_of(label),
                     {"protocol_id": protos[(s, t, sp)], "dataset_version": "ViroBench (arXiv 2605.25388v1)", "split": f"{sp_label} test partition",
                      "population": None, "inputs": "Viral nucleotide sequence windows of 512, 1024 or 2048 bp",
                      "adaptation": "Frozen embeddings with a standardised MLP head" if family(label) not in ("BLAST", "Kraken2", "ViroBench BiLSTM baseline", "ViroBench CNN baseline") else "Baseline as configured by the benchmark authors",
                      "metric_implementation": "Macro-F1 x100 as printed",
                      "aggregation": "Mean across hyperparameter settings (window configurations and learning rates)", "budget": None},
                     f"{table} row '{label}', column '{SETS[s]} / {t} / {sp_label}'")
        loc = f"{table}, row '{label}', column '{SETS[s]} / {t} / {sp_label}' (text-layer line {ln})"
        printed = f"{mean} ({sd})"
        unc = {"type": "standard_deviation", "value": sd, "printed": f"({sd})",
               "scope": "Across hyperparameter settings (window configurations and learning rates), Section 4.1.2"}
        b.result(b.rid("result", label, s, t, sp_label), f"{label} {SETS[s]} {t} {sp_label}", SRC, SIDS, e, printed, "macro-f1", "higher", "percent",
                 loc, REVIEW(f"{table}, text-layer line {ln}."), qualifier=f"ViroBench {SETS[s]}, {t.lower()}, {sp_label}",
                 unit_detail="Macro-F1 x100 as printed", uncertainty=unc, numeric=num(mean),
                 extra={"printed_value_basis": "Mean followed by the standard deviation in parentheses, as printed"})

for r in rows25:
    add_row("Table 25", *r)
for r in extra4:
    add_row("Table 4", *r)

# ---------------------------------------------------------------------------
# Corrections from the independent review (reviewer-mi-1, 2026-10-11), applied
# verbatim from docs/reviews/2026-10-11-microbial-interactions-lit.md. Labels V1
# to V4 are the reviewer's.
# ---------------------------------------------------------------------------
REVIEWER_NOTE = ("Claude review agent reviewer-mi-1, independent of the extractor "
                 "lit-microbial-interactions; no human review claimed")
RSHA = SHA

# V1 and V2: two source-level evidence concerns.
CONCERNS = [
    {"source_id": SRC,
     "message": ("Table 25 prints one Macro-F1 per model for the taxonomy columns. For 143 of the 144 "
                 "model-by-split taxonomy cells on the ALL-virus set, the printed value equals the mean of "
                 "the five per-rank values in Table 26 rounded to two decimals. The exception is RNA-FM "
                 "under the genus-disjoint split: Table 25 prints 48.67 and the mean of the Table 26 ranks "
                 "(59.96, 65.35, 37.58, 58.78, 43.82) is 53.10. One of the two tables is wrong for that "
                 "row, so RNA-FM ALL taxonomy G-Split should not be used in a comparison without checking "
                 "the published code."),
     "source_locator": "Table 25, row 'RNA-FM', column 'ALL viruses / Taxonomy / G-Split'; Table 26, row 'RNA-FM'",
     "artifact_sha256": RSHA, "reviewed_at": "2026-10-11T00:00:00Z", "review_method": "ai-assisted-source-review"},
    {"source_id": SRC,
     "message": ("Table 3 lists NT v3 under phage-specific pretraining coverage (P) and Table 9 lists it as "
                 "non-viral (N). Table 25 groups the NTv3 rows under phage-specific coverage, which is what "
                 "the configurations record. Pretraining coverage is the paper's main explanatory variable, "
                 "so NT v3 rows should not be used to support a coverage-versus-performance claim."),
     "source_locator": "Table 3 row 'NT v3'; Table 9 row 'NT v3'; Table 25 section 'DNA Foundation Models (Phage-specific Coverage)'",
     "artifact_sha256": RSHA, "reviewed_at": "2026-10-11T00:00:00Z", "review_method": "ai-assisted-source-review"},
]
by_id = {r["id"]: r for r in b.records}
by_id[SRC]["attributes"]["evidence_concerns"] = CONCERNS

# V3: the taxonomy protocols say what is and is not known about the rank aggregation.
V3_ALL = ("The taxonomy column is a single Macro-F1 per model; the source predicts five ranks (Kingdom to "
          "Family) through five parallel heads (Appendix B.3) and never states how the ranks are combined. "
          "On the ALL-virus set the printed value equals the rounded mean of the five Table 26 per-rank "
          "values for 143 of 144 cells, the exception being RNA-FM under the genus-disjoint split. The mean "
          "is an observation about the printed numbers, not a stated aggregation, and no value was computed "
          "from it.")
V3_OTHER = V3_ALL + (" Table 26, the per-rank table, covers the ALL-virus set only, so the aggregation "
                     "cannot be checked for the DNA and RNA virus sets.")
# V4: the source's own single-label caveat on host classification.
V4 = ("Host classification assigns each virus to exactly one coarse-grained host category; the source says "
      "many viruses have multi-host tropism and that single-label framing can penalise biologically "
      "reasonable secondary host associations (Appendix limitations discussion, text-layer lines 2185 to 2199).")
n_tax, n_host = 0, 0
for (s_set, t, sp) in COLS:
    pid = protos[(s_set, t, sp)]
    lims = by_id[pid]["attributes"]["limitations"]
    if t == "Taxonomy":
        hits = [i for i, l in enumerate(lims) if l.startswith("The taxonomy column is a single Macro-F1 per model")]
        assert len(hits) == 1, (pid, lims)
        lims[hits[0]] = V3_ALL if s_set == "ALL" else V3_OTHER
        n_tax += 1
    else:
        assert not any(l.startswith("Host classification assigns") for l in lims)
        lims.append(V4)
        n_host += 1
assert n_tax == 6 and n_host == 6, (n_tax, n_host)

# Review blocks: the reviewer's own checks, recorded on every result and on the source.
R_METHODS = ["source-hash-verification", "pdf-text-parse", "independent-cell-check", "rendered-source-visual-check"]
R_NOTE = ("Re-downloaded the arXiv PDF and matched its SHA-256 and the text-layer hash, including against the "
          "archived gzip. Parsed every cell of Table 25 (74 rows x 12) and Table 4 (34 rows) with an "
          "independent parser and matched all 912 results by source_locator: printed values, numeric values, "
          "standard deviations and text-layer line numbers all match, with no duplicate or missing cell. "
          "Every Table 4 row also present in Table 25 agrees cell for cell, and the two rows unique to "
          "Table 4 agree with Table 19. Read 79 cells by eye from pages rendered at 150 and 400 dpi, "
          "covering both Table 25 pages, all four baselines, all coverage groups, both tasks, both splits, "
          "all three virus sets and models from 1M to 40B parameters: 79 of 79 confirmed.")
for r in b.records:
    if r["kind"] == "result":
        old = r["attributes"]["review"]
        r["attributes"]["review"] = reviewed_review(R_METHODS, R_NOTE, REVIEWER_NOTE, SHA, URL,
                                                    old["method_note"], R_NOTE)
by_id[SRC]["attributes"]["review"] = source_review(
    REVIEWER_NOTE,
    "PDF re-downloaded and its SHA-256 matched; pdftotext -layout rerun and the text-layer hash matched the "
    "record and the archived gzip.")
mark_reviewed(b)

counts = b.write()
print(json.dumps(counts), "rows25", len(rows25), "extra4", len(extra4))
