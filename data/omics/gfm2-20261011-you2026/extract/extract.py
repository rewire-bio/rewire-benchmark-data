"""Build the You et al. 2026 batch from the pinned Nature Communications supplementary information.

Usage: python3 -I extract.py <supp1.txt from `pdftotext -layout 41467_2025_66899_MOESM1_ESM.pdf`>
Parses Supplementary Tables 4 and 5 (splicing tasks) with method and column labels asserted.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lit-search-20261011-gfm-2" / "extract"))
from gfm2lib import Batch  # noqa: E402

P = "gfm2-20261011-you2026"
SRC = f"{P}-source"
SUPP = f"{P}-source-supplement"
ART_SHA = "2c6b2816846a21296c56b4dd58f3d1e8810e9d96e224d3ab21b5eb8faa9928e4"
SUPP_SHA = "cbb69e05045a4526e35479d2c1361ebb9cfadfd968e00675390dad597035d882"
ART_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12780105/fullTextXML"
SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12780105/supplementaryFiles"
NOTE = ("Deterministic parse of `pdftotext -layout` (poppler 26.08.0) text of the pinned supplementary PDF, with the "
        "task block, method label and column order asserted (extract/extract.py). Pending independent review.")

lines = Path(sys.argv[1]).read_text().splitlines()

b = Batch(P, SRC)
b.source("Benchmarking pre-trained genomic language models for RNA sequence-related predictive applications",
         "Nature Communications article benchmarking eleven pre-trained genomic language models against task-specific methods on non-coding RNA classification, m6A modification, splice site prediction and translation efficiency.",
         {"url": "https://doi.org/10.1038/s41467-025-66899-y", "doi": "10.1038/s41467-025-66899-y",
          "artifact_url": ART_URL, "artifact_sha256": ART_SHA, "retrieved_at": "2026-10-11T00:55:34Z",
          "publication_status": "peer_reviewed", "version": "Nat Commun 17:223, published online 2025-12-07; PMC12780105 full-text XML",
          "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml",
          "source_locator": "Methods; Table 1; Supplementary Information"})
b.add({"id": SUPP, "kind": "source", "name": "You et al. 2026, Supplementary Information",
       "description": "Supplementary Tables 1-6 of the article, holding the per-method performance tables behind the figures.",
       "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["research"]}, "source_ids": [], "links": [],
       "attributes": {"url": "https://doi.org/10.1038/s41467-025-66899-y", "doi": "10.1038/s41467-025-66899-y",
                      "artifact_url": SUPP_URL, "artifact_sha256": SUPP_SHA, "retrieved_at": "2026-10-11T00:55:34Z",
                      "publication_status": "peer_reviewed",
                      "version": "41467_2025_66899_MOESM1_ESM.pdf inside the Europe PMC supplementaryFiles zip (outer zip 9a0d0a8d8643872ab265e3e6ed7eea944563da4861bf764f97c68fc6aa502525, assembled per request; the member hash is the bound artifact)",
                      "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf",
                      "source_locator": "Supplementary Tables 4 and 5"}})
SOURCES = [SRC, SUPP]

# Families. Only the DNA-side families are reused from the store; RNA language models and
# task-specific methods get new family records at the level the source names them.
FAMILIES = {
    "DNABERT": ("DNABERT", "method", "DNA language model with k-mer tokenisation (You et al. 2026 Table 1)."),
    "DNABERT2": ("DNABERT-2", "reuse:discovery-model-dnabert-2", ""),
    "NucleotideTransformer": ("Nucleotide Transformer", "reuse:discovery-model-nucleotide-transformer", ""),
    "GENA-LM-base": ("GENA-LM", "model", "DNA language model family with byte-pair tokenisation and long context (You et al. 2026 Table 1)."),
    "GENA-LM-large": ("GENA-LM", "same:GENA-LM-base", ""),
    "SpliceBERT": ("SpliceBERT", "model", "Pre-trained language model of precursor mRNA sequence (You et al. 2026 Table 1)."),
    "RNAFM": ("RNA-FM", "model", "RNA language model pre-trained on non-coding RNA sequence (You et al. 2026 Table 1)."),
    "RNAMSM": ("RNA-MSM", "model", "RNA language model pre-trained on multiple sequence alignments (You et al. 2026 Table 1)."),
    "RNAErnie": ("RNAErnie", "model", "RNA language model with motif-aware pre-training (You et al. 2026 Table 1)."),
    "RNABERT": ("RNABERT", "model", "RNA language model pre-trained on small non-coding RNA (You et al. 2026 Table 1)."),
    "UTRLM": ("UTR-LM", "model", "Language model pre-trained on 5' untranslated region sequence (You et al. 2026 Table 1)."),
    "SpTransformer": ("SpTransformer", "method", "Task-specific transformer for tissue-specific splice site prediction (You et al. 2026 Introduction)."),
    "SpliceAI": ("SpliceAI", "reuse:discovery-model-spliceai", ""),
}

family_ids = {}
for key, (name, how, desc) in FAMILIES.items():
    if how.startswith("reuse:"):
        family_ids[key] = how.split(":", 1)[1]
    elif how.startswith("same:"):
        family_ids[key] = family_ids[how.split(":", 1)[1]]
    elif how == "model":
        family_ids[key] = b.model(name.lower().replace(" ", "-").replace("'", ""), name, desc,
                                  "Table 1 'Summary of language models'; Methods")
    else:
        family_ids[key] = b.method(name.lower().replace(" ", "-"), name, desc,
                                   "Table 1 'Summary of language models'; Introduction")
for r in b.records.values():
    if r["kind"] in ("model", "method"):
        r["source_ids"] = SOURCES

IS_LM = {k for k in FAMILIES if k not in ("SpTransformer", "SpliceAI")}
VERSION_MISSING = {"reason": "unreported", "note": "Checkpoint revision not printed; fine-tuning parameters are in Supplementary Table 1"}

configs = {}
for key in FAMILIES:
    printed = key
    lm = key in IS_LM
    configs[key] = b.config(
        key, f"{printed} fine-tuned with an appended convolution head, 500 bp input (You et al. 2026)" if lm
        else f"{printed} as distributed, 500 bp input (You et al. 2026)",
        family_ids[key], "foundation_model" if lm else "specialist", printed,
        f"Methods, 'Construction of tissue-specific alternative splicing prediction task'; Supplementary Tables 4 and 5, row '{printed}'",
        version_missing=VERSION_MISSING,
        parameters=("Pre-trained backbone with a convolution layer appended to derive per-nucleotide scores; AdamW; input divided into 500 bp sequences; fine-tuned and tested three times with different random initialisations"
                    if lm else
                    "Task-specific model run on the same 500 bp input split, fine-tuned and tested three times with different random initialisations"),
        extra={"training_setting": "Fine-tuned on the task training split"}, fm=lm)
for r in b.records.values():
    if r["kind"] == "configuration":
        r["source_ids"] = SOURCES

LIM = ["Fine-tuned and tested three times with different random initialisations; the printed spread is the standard deviation over those three runs (Methods, 'To ensure the reliability of our findings').",
       "All methods are given a 500 bp input so that models with different context windows are comparable; SpTransformer and SpliceAI were designed for 1,000 to 5,000 nucleotide inputs (Results).",
       "Each language model is fine-tuned with an appended convolution head, so the comparison measures the adapted model, not zero-shot likelihood.",
       "Values are read from the Supplementary Information tables behind the figures; the main-text figures are not read."]

DATA = {
    "NT-splice-sites-all": ("nt-splice-all", "Nucleotide Transformer benchmark splice-site dataset, all sites",
                            "Splice-site classification data covering 5 species and 3 categories: 30,000 sequences, 27,000 train and 3,000 test.",
                            "5 species, 3 categories; 30,000 sequences", "27,000 train / 3,000 test", 30000),
    "NT-splice-sites-acceptors": ("nt-splice-acceptors", "Nucleotide Transformer benchmark splice-site dataset, acceptors",
                                  "Acceptor-site classification data covering 147 species and 2 categories: 22,179 sequences, 19,961 train and 2,218 test.",
                                  "147 species, 2 categories; 22,179 sequences", "19,961 train / 2,218 test", 22179),
    "NT-splice-sites-donors": ("nt-splice-donors", "Nucleotide Transformer benchmark splice-site dataset, donors",
                               "Donor-site classification data covering 147 species and 2 categories: 21,973 sequences, 19,775 train and 2,198 test.",
                               "147 species, 2 categories; 21,973 sequences", "19,775 train / 2,198 test", 21973),
}
data_ids = {}
for name, (key, dname, desc, pop, split, total) in DATA.items():
    data_ids[name] = b.dataset(key, dname, desc,
                               {"version": f"As used by You et al. 2026 (Table 1, '{name}')", "split": split,
                                "population": pop, "total": total,
                                "source_locator": f"Table 1, 'Splicing prediction', row '{name}'"})
gtex = b.dataset("gtex", "GTEx-derived tissue-specific splice site usage dataset (You et al. 2026)",
                 "Human splice site usage across tissues derived from GTEx: 341,830 entries, 242,017 train and 99,813 test, with 53 categories.",
                 {"version": "As constructed by You et al. 2026 from GTEx", "split": "242,017 train / 99,813 test",
                  "population": "Human; 53 categories; 341,830 entries", "total": 341830,
                  "source_locator": "Table 1, 'Splicing prediction', row 'GTEx Dataset'; Methods, 'Construction of tissue-specific alternative splicing prediction task'"})
for r in b.records.values():
    if r["kind"] == "dataset":
        r["source_ids"] = SOURCES

T4_METRICS = [("F1 Score", "f1-score", "fraction"), ("Precision", "precision", "fraction"),
              ("Recall", "recall", "fraction"), ("Accuracy", "accuracy", "fraction")]
T5_METRICS = [("Average PR-AUC", "auprc", "fraction"), ("Average Top-k", "splice-top-k-accuracy", "fraction")]
CELL = re.compile(r"(\d\.\d{4})\((\d\.\d{4})\)")


def block(start_text, stop_texts):
    i = next(k for k, l in enumerate(lines) if start_text in l)
    j = min([k for k in range(i + 1, len(lines)) if any(s in lines[k] for s in stop_texts)] or [len(lines)])
    return lines[i + 1:j]


def parse(rows, n_metrics):
    out = []
    for line in rows:
        cells = CELL.findall(line)
        if len(cells) != n_metrics:
            continue
        label = line.strip().split()[0]
        out.append((label, cells))
    return out


# Supplementary Table 4: the three Nucleotide Transformer splice-site datasets.
t4 = block("NT-splice-sites-all", ["Supplementary Table 4"])
sections = {}
current = "NT-splice-sites-all"
sections[current] = []
for line in t4:
    s = line.strip()
    if s in ("NT-splice-sites-acceptors", "NT-splice-sites-donors"):
        current = s
        sections[current] = []
    else:
        sections[current].append(line)

p4 = {}
for name in DATA:
    p4[name] = b.protocol(
        DATA[name][0], f"{name} splice-site classification, 500 bp input, fine-tuned models (You et al. 2026 Supplementary Table 4)",
        "Classification of splice sites on the Nucleotide Transformer benchmark dataset, with every method given the same 500 bp input and the same train/test split.",
        {"protocol": "Fine-tune each model on the dataset's training split with an appended convolution head for the language models, then score the held-out test split. Each model is fine-tuned and tested three times with different random initialisations; mean and standard deviation are reported.",
         "version": f"Supplementary Table 4, block '{name}'", "metric_direction": "higher", "unit": "fraction",
         "aggregation": "Mean over three fine-tuning runs", "replicates": "Three random initialisations",
         "metric_implementation": "F1 score, precision, recall and accuracy as defined in Methods",
         "limitations": LIM, "source_locator": f"Supplementary Table 4, block '{name}'; Table 1; Methods"},
        data_id=data_ids[name])

for name, rows in sections.items():
    for label, cells in parse(rows, 4):
        assert label in FAMILIES, (name, label)
        ev = b.evaluation(f"t4-{DATA[name][0]}-{label}", f"{label} on {name}, 500 bp input",
                          configs[label], p4[name], data_ids[name],
                          "independent_paper" if label in IS_LM else "independent_paper",
                          {"dataset_version": f"{name} as used by You et al. 2026", "split": DATA[name][4],
                           "population": DATA[name][3], "inputs": "500 bp DNA sequence",
                           "adaptation": "Fine-tuned with an appended convolution head" if label in IS_LM else "Fine-tuned task-specific model",
                           "metric_implementation": "F1 score, precision, recall and accuracy",
                           "aggregation": "Mean over three fine-tuning runs"},
                          f"Supplementary Table 4, block '{name}', row '{label}'", limitations=LIM)
        ev_rec = b.records[ev]
        ev_rec["source_ids"] = SOURCES
        for (column, metric, unit), (value, sd) in zip(T4_METRICS, cells):
            rid = b.result(f"t4-{DATA[name][0]}-{label}-{column}", ev, metric, f"{value}({sd})",
                           f"Supplementary Table 4, block '{name}', row '{label}', column '{column}'",
                           unit=unit, qualifier=f"{name}, 500 bp input, fine-tuned",
                           uncertainty={"type": "standard_deviation", "value": sd, "printed": f"({sd})", "n": 3,
                                        "scope": "Three fine-tuning runs with different random initialisations"},
                           method_note=NOTE)
            b.records[rid]["source_ids"] = SOURCES
            b.records[rid]["attributes"]["numeric_value"] = value

# Supplementary Table 5: GTEx tissue-specific splicing prediction, three task settings.
t5 = block("Splice acceptors and donors", ["Supplementary Table 5"])
T5_SECTIONS = {"acceptors-donors": ("Splice acceptors and donors", "Acceptor and donor sites, pooled"),
               "splice-15class": ("Splice-15class", "Splice site usage across 15 human tissues"),
               "splice-53class": ("Splice-53class", "Splice site usage across 53 categories")}
t5_blocks = {"acceptors-donors": []}
current = "acceptors-donors"
for line in t5:
    s = line.strip()
    if s == "Splice-15class":
        current = "splice-15class"
        t5_blocks[current] = []
    elif s == "Splice-53class":
        current = "splice-53class"
        t5_blocks[current] = []
    else:
        t5_blocks[current].append(line)

for key, (printed, desc) in T5_SECTIONS.items():
    pid = b.protocol(f"gtex-{key}", f"GTEx tissue-specific splicing prediction, {printed} (You et al. 2026 Supplementary Table 5)",
                     f"{desc}: every method scores all splice sites within the central 500 bp of the input sequence.",
                     {"protocol": "Score all potential splice sites within the centre 500 bp of each input sequence from the GTEx-derived dataset; fine-tune and test three times with different random initialisations and report mean and standard deviation of average PR-AUC and average top-k accuracy.",
                      "version": f"Supplementary Table 5, block '{printed}'", "metric_direction": "higher", "unit": "fraction",
                      "aggregation": "Mean over three fine-tuning runs; metrics averaged over the task's output categories",
                      "replicates": "Three random initialisations",
                      "metric_implementation": "Average PR-AUC and SpliceAI-style top-k accuracy, chosen because splice sites are sparse and the classes extremely imbalanced (Results)",
                      "limitations": LIM + ["Not every method appears in every block: the 15- and 53-class blocks list seven methods and the pooled acceptor and donor block eight."],
                      "source_locator": f"Supplementary Table 5, block '{printed}'; Methods"},
                     data_id=gtex)
    b.records[pid]["source_ids"] = SOURCES
    for label, cells in parse(t5_blocks[key], 2):
        assert label in FAMILIES, (key, label)
        ev = b.evaluation(f"t5-{key}-{label}", f"{label} on the GTEx splicing task, {printed}",
                          configs[label], pid, gtex, "independent_paper",
                          {"dataset_version": "GTEx-derived dataset as constructed by You et al. 2026",
                           "split": "242,017 train / 99,813 test", "population": "Human; 341,830 entries",
                           "inputs": "500 bp DNA sequence, scoring all sites in the central 500 bp",
                           "adaptation": "Fine-tuned with an appended convolution head" if label in IS_LM else "Fine-tuned task-specific model",
                           "metric_implementation": "Average PR-AUC and average top-k accuracy",
                           "aggregation": "Mean over three fine-tuning runs"},
                          f"Supplementary Table 5, block '{printed}', row '{label}'", limitations=LIM)
        b.records[ev]["source_ids"] = SOURCES
        for (column, metric, unit), (value, sd) in zip(T5_METRICS, cells):
            rid = b.result(f"t5-{key}-{label}-{column}", ev, metric, f"{value}({sd})",
                           f"Supplementary Table 5, block '{printed}', row '{label}', column '{column}'",
                           unit=unit, qualifier=f"GTEx splicing task, {printed}, averaged over categories",
                           uncertainty={"type": "standard_deviation", "value": sd, "printed": f"({sd})", "n": 3,
                                        "scope": "Three fine-tuning runs with different random initialisations"},
                           method_note=NOTE)
            b.records[rid]["source_ids"] = SOURCES
            b.records[rid]["attributes"]["numeric_value"] = value

b.claim("not-extracted", SUPP, "tables_not_extracted",
        "Supplementary Tables 2 (non-coding RNA classification), 3 (m6A modification), 6 (translation efficiency) and the main-text figures are not extracted in this batch; only the splicing tables 4 and 5 are.",
        "Supplementary Tables 2, 3 and 6")
b.records[b.rid("claim", "not-extracted")]["source_ids"] = SOURCES

counts = b.write(HERE.parent)
print(counts, sum(counts.values()))
