"""Build the Bůžková et al. 2026 batch from the pinned bioRxiv PDF.

Usage: python3 -I extract.py <article.txt from `pdftotext -layout article.pdf`>
Parses Tables 3, 7, 8, 9 and 10 with asserted row and column labels.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lit-search-20261011-gfm-2" / "extract"))
from gfm2lib import Batch, table_rows  # noqa: E402

P = "gfm2-20261011-buzkova2026"
SRC = f"{P}-source"
SHA = "9a589a2088f8466502b1035228db3e594065e984e5755c25d907471225f75c19"
URL = "https://www.biorxiv.org/content/10.64898/2026.09.25.754388v1.full.pdf"
NOTE = ("Deterministic parse of `pdftotext -layout` (poppler 26.08.0) text of the pinned PDF with row and column "
        "labels asserted (extract/extract.py). Pending independent review.")

lines = [l for l in Path(sys.argv[1]).read_text().splitlines()
         if "bioRxiv preprint doi" not in l and "preprint (which was not" not in l and "is made available under" not in l]

b = Batch(P, SRC)
b.source(
    "Analyzing Genomic Foundation Models for Viral Sequence Identification",
    "bioRxiv preprint v1 comparing frozen Nucleotide Transformer and DNABERT embeddings with nearest-neighbour search against BLAST on RVDB-derived viral classification.",
    {"url": "https://doi.org/10.64898/2026.09.25.754388", "doi": "10.64898/2026.09.25.754388", "artifact_url": URL,
     "artifact_sha256": SHA, "retrieved_at": "2026-10-11T00:48:35Z", "publication_status": "preprint",
     "version": "bioRxiv v1, posted 2026-09-28", "licence": "CC-BY-4.0", "media_type": "application/pdf",
     "source_locator": "Full text PDF, 27 pages; Tables 1-10"})

# Models and methods. Existing records are reused where they name the same family.
NT_FAMILY = "discovery-model-nucleotide-transformer"
NT_V2 = "catalog-model-nt-v2"
DNABERT2 = "discovery-model-dnabert-2"
BLAST = "dna-pathogen-20261009-method-blast"
dnabert_s = b.model("dnabert-s", "DNABERT-S", "Species-aware DNA embedding model contrastively fine-tuned from DNABERT-2 (Bůžková et al. 2026 Table 2).",
                    "Section 2.3; Table 2, row 'DNABERT-S'")

TABLE2 = {  # reported name: (parameters, context, tokenizer, training data) as printed in Table 2
    "NTv1": ("NTv1 (Multispecies 2.5B)", NT_FAMILY, "2.5B", "1,000", "6-mer", "850-species genomes"),
    "NTv2-50M": ("NTv2-50M", NT_V2, "50M", "2,048", "6-mer", "850-species genomes"),
    "NTv2-250M": ("NTv2-250M", NT_V2, "250M", "2,048", "6-mer", "850-species genomes"),
    "NTv2-500M": ("NTv2-500M", NT_V2, "500M", "2,048", "6-mer", "850-species genomes"),
    "NTv3-8M": ("NTv3-8M", NT_FAMILY, "8M", "1 Mb", "Single-base", "OpenGenome2"),
    "NTv3-100M": ("NTv3-100M", NT_FAMILY, "100M", "1 Mb", "Single-base", "OpenGenome2"),
    "NTv3-650M": ("NTv3-650M", NT_FAMILY, "650M", "1 Mb", "Single-base", "OpenGenome2"),
    "DNABERT-2": ("DNABERT-2", DNABERT2, "117M", "512; flex.", "BPE (4,096)", "135-species genomes"),
    "DNABERT-S": ("DNABERT-S", dnabert_s, "117M", "512; flex.", "BPE (4,096)", "135-species genomes"),
}
t2 = table_rows(lines, "Table 2. Overview of the evaluated models", "2.4 Embedding generation and pooling")
for key, (printed, _, params, ctx, tok, data) in TABLE2.items():
    row = next(l for l in t2 if l.strip().startswith(printed + " ") or l.strip().startswith(printed + "  "))
    for cell in (params, ctx, tok, data):
        assert cell in row, (key, cell, row)

POOLINGS = [("mean-all", "Mean, all tokens"), ("mean-excl", "Mean, special tokens excluded"),
            ("max-all", "Max, all tokens"), ("max-excl", "Max, special tokens excluded"), ("cls", "CLS token only")]
VERSION_MISSING = {"reason": "unreported", "note": "Official Hugging Face repository named but no revision is printed (Section 2.4)"}

configs = {}
for key, (printed, of, params, ctx, tok, data) in TABLE2.items():
    for pkey, plabel in POOLINGS:
        if key.startswith("NTv3") and pkey in ("mean-excl", "max-excl", "cls"):
            continue
        cid = b.config(f"{key}-{pkey}", f"{printed}, frozen embeddings, {plabel.lower()} pooling, 1-NN (Bůžková et al. 2026)",
                       of, "foundation_model", printed, f"Table 2 row '{printed}'; Table 3 column '{key}', row '{plabel}'",
                       version_missing=VERSION_MISSING,
                       parameters=f"{params} parameters; context {ctx}; {tok} tokenizer; frozen weights; {plabel} pooling; L2-normalised embeddings, FAISS IndexFlatIP, k = 1",
                       extra={"training_setting": "Frozen weights, no parameter update; nearest-neighbour probe over labelled reference embeddings"})
        configs[(key, pkey)] = cid
    b.claim(f"{key}-table2", configs[(key, "mean-all")], "model_characteristics",
            f"{printed}: {params} parameters; context {ctx}; tokenizer {tok}; training data {data}",
            f"Table 2, row '{printed}'")

blastn = b.config("blastn", "BLAST 2.12.0 blastn, top hit (Bůžková et al. 2026)", BLAST, "conventional_pipeline", "blastn",
                  "Section 2.8; Tables 7, 8 and 10", version="BLAST 2.12.0", fm=False,
                  parameters="Custom nucleotide database from the training FASTA; task blastn; max_target_seqs = 1; label of the top hit")
megablast = b.config("megablast", "BLAST 2.12.0 megablast, top hit (Bůžková et al. 2026)", BLAST, "conventional_pipeline",
                     "megablast", "Section 2.8; Table 7", version="BLAST 2.12.0", fm=False,
                     parameters="Custom nucleotide database from the training FASTA; task megablast; max_target_seqs = 1; label of the top hit")

# Datasets
d33 = b.dataset("rvdb-33", "RVDB C-RVDB v31.0 primary dataset, 33 refined classes",
                "Viral sequences up to 2,046 bp from the clustered Reference Viral DataBase v31.0, 500 per class, split 70/30 stratified by class; 40 sampled classes refined to 33 after removing taxonomically ambiguous labels.",
                {"version": "C-RVDB v31.0, 9 January 2026", "split": "70/30 train/test, stratified by class; 350 indexed and 150 queried per class",
                 "population": "16,500 sequences; 4,950 test queries", "total": 16500,
                 "source_locator": "Section 2.2; Table 1 column 'Primary dataset'"})
d40 = b.dataset("rvdb-40", "RVDB C-RVDB v31.0 primary dataset, 40 sampled classes",
                "The same primary dataset before the taxonomic refinement, with all 40 randomly sampled organism classes.",
                {"version": "C-RVDB v31.0, 9 January 2026", "split": "70/30 train/test, stratified by class; 350 indexed and 150 queried per class",
                 "population": "20,000 sequences; 6,000 test queries", "total": 20000,
                 "source_locator": "Section 2.2; Table 1 column 'Primary dataset'"})
dlong = b.dataset("rvdb-long", "RVDB C-RVDB v31.0 long-sequence dataset, 16 classes",
                  "Viral sequences above 50,000 bp (test sequences 84,587 to 409,110 bp) from 16 manually reviewed classes, with the split inverted to about 20% indexed and 80% queried.",
                  {"version": "C-RVDB v31.0, 9 January 2026", "split": "About 4 indexed and about 16 queried sequences per class; 256 test sequences",
                   "population": "About 320 sequences; 256 test queries", "total": 320,
                   "source_locator": "Section 2.2; Table 1 column 'Long-sequence dataset'; Table 10 legend"})

LIM_NN = ["Nearest-neighbour probe over labelled reference embeddings, not zero-shot classification: the index holds the training labels (Section 2.7).",
          "Point estimates from one fixed split with a fixed random seed; 95% Wilson intervals are quoted in the text, not in the tables.",
          "RVDB organism labels are not a controlled taxonomy; the 33-class refinement removed seven ambiguous labels found through the models' own confusions (Sections 3.2 and 4)."]

p33 = b.protocol("acc-33", "RVDB 33-class viral classification by nearest-neighbour retrieval over frozen embeddings (Bůžková et al. 2026 Table 3)",
                 "Assign the organism label of the single nearest indexed training sequence to each test sequence, comparing pooling strategies across nine models.",
                 {"protocol": "Generate one frozen embedding per sequence by the stated pooling, L2-normalise, index the training embeddings with FAISS IndexFlatIP, retrieve the nearest neighbour (k = 1) for each test sequence and take its label. No parameter update.",
                  "version": "Table 3 (33-class dataset, maximum length 2,046 bp)", "metric": "accuracy", "metric_direction": "higher", "unit": "fraction",
                  "aggregation": "Share of the 4,950 test sequences labelled correctly",
                  "metric_implementation": "Accuracy over test sequences; macro F1, precision and recall reported separately in Table 7",
                  "limitations": LIM_NN, "source_locator": "Table 3; Sections 2.7 and 3.1"}, data_id=d33)

p_blast = b.protocol("blast-compare", "RVDB viral classification: best frozen-embedding configuration against BLAST (Bůžková et al. 2026 Table 7)",
                     "Accuracy, macro F1, precision and recall for blastn, megablast and the best foundation-model configuration on the 40- and 33-class datasets.",
                     {"protocol": "Both pipelines index the same 350 training sequences per class. BLAST builds a nucleotide database from the training FASTA and takes the top hit's label (max_target_seqs = 1); the foundation model retrieves the nearest frozen embedding. Neither can return a label outside the reference set.",
                      "version": "Table 7 (max_target_seqs = 1)", "metric_direction": "higher", "unit": "fraction",
                      "aggregation": "Accuracy over test sequences; F1, precision and recall macro-averaged over classes",
                      "limitations": LIM_NN + ["Only the best foundation-model configuration (NTv3-650M, max pooling) appears in this table."],
                      "source_locator": "Table 7; Sections 2.8, 2.9 and 3.6"}, data_id=d33)

p_long = b.protocol("long", "RVDB long-sequence viral classification, 16 classes (Bůžková et al. 2026 Table 10)",
                    "Classification of 84.6 to 409 kb viral genomes from about four indexed sequences per class, for four foundation models and blastn.",
                    {"protocol": "As for the primary dataset, but with about 4 indexed and about 16 queried sequences per class. NTv3-650M and blastn process each sequence whole; DNABERT-2, NTv2-50M and NTv2-250M are scored over overlapping chunks because their context window is shorter than these genomes.",
                     "version": "Table 10 (16 classes, 256 test sequences)", "metric_direction": "higher", "unit": "fraction",
                     "aggregation": "Pooled over test sequences; balanced accuracy, MCC and macro F1, precision and recall also reported",
                     "limitations": LIM_NN + ["Chunk-scored rows (DNABERT-2, NTv2-50M, NTv2-250M) are not computed on the same unit as the whole-sequence rows (Table 10 footnote a).",
                                              "256 test sequences: the interval half-width near an accuracy of 0.95 is about 0.026, and the authors state the narrowing against BLAST is indicative only (Sections 2.9 and 3.8).",
                                              "The long-sequence classes are more divergent viruses than the primary dataset's closely related subtypes, so dataset difficulty differs in more than sequence length (Section 4)."],
                     "source_locator": "Table 10; Section 3.8"}, data_id=dlong)

# Table 3: nine models x five pooling configurations.
t3 = table_rows(lines, "Table 3. Accuracy for all models across pooling configurations", "3.2 Taxonomic ambiguity")
header = next(l for l in t3 if "NTv1" in l and "DNABERT-" in l)
order = ["NTv1", "NTv2-50M", "NTv2-250M", "NTv2-500M", "NTv3-8M", "NTv3-100M", "NTv3-650M", "DNABERT-2", "DNABERT-S"]
cell = re.compile(r"⋆?\d\.\d{4}|—")
pool_markers = {"mean-all": "Mean, all", "mean-excl": "Mean, special", "max-all": "Max, all", "max-excl": "Max, special", "cls": "CLS token"}
for pkey, plabel in POOLINGS:
    row = next(l for l in t3 if l.strip().startswith(pool_markers[pkey]))
    cells = cell.findall(row)
    assert len(cells) == 9, (pkey, cells)
    for model, printed in zip(order, cells):
        if printed == "—":
            continue
        cfg = configs[(model, pkey)]
        ev = b.evaluation(f"t3-{model}-{pkey}", f"{TABLE2[model][0]}, {plabel.lower()} pooling, on the RVDB 33-class dataset",
                          cfg, p33, d33, "independent_paper",
                          {"dataset_version": "C-RVDB v31.0 primary dataset, 33 refined classes",
                           "split": "350 indexed and 150 queried sequences per class",
                           "population": "4,950 test sequences",
                           "inputs": "Nucleotide sequence up to 2,046 bp",
                           "adaptation": f"None: frozen weights, {plabel.lower()} pooling, 1-NN over the indexed training embeddings",
                           "metric_implementation": "Accuracy over test sequences",
                           "aggregation": "Pooled over test sequences"},
                          f"Table 3, column '{model}', row '{plabel}'",
                          limitations=["Independent evaluation; the authors develop none of the models compared."])
        star = " The printed cell carries the table's overall-best marker, kept in printed_value." if printed.startswith("\u22c6") else ""
        b.result(f"t3-{model}-{pkey}", ev, "accuracy", printed,
                 f"Table 3, column '{model}', row '{plabel}'", qualifier="33-class RVDB dataset, 1-NN over frozen embeddings",
                 method_note=NOTE, note="Extraction only; pending independent review." + star)

# Table 7: BLAST against the best foundation-model configuration.
t7 = table_rows(lines, "Table 7. Comparison of BLAST with the best GFM configuration", "3.7 Robustness to mutation and masking")
T7_ROWS = [("40", "blastn", blastn, d40), ("40", "megablast", megablast, d40), ("40", "NTv3-650M (max)", configs[("NTv3-650M", "max-all")], d40),
           ("33", "blastn", blastn, d33), ("33", "megablast", megablast, d33), ("33", "NTv3-650M (max)", configs[("NTv3-650M", "max-all")], d33)]
T7_METRICS = [("Accuracy", "accuracy", None), ("F1", "macro-f1", None), ("Precision", "precision", "macro-averaged over classes"),
              ("Recall", "recall", "macro-averaged over classes")]
seen7 = set()
for classes, label, cfg, data in T7_ROWS:
    row = next(l for i, l in enumerate(t7)
               if l.strip().startswith(f"{classes} classes") and label in l and (classes, label) not in seen7)
    seen7.add((classes, label))
    cells = re.findall(r"0\.\d{4}", row)
    assert len(cells) == 4, (classes, label, row)
    ev = b.evaluation(f"t7-{classes}-{label}", f"{label} on the RVDB {classes}-class dataset (BLAST comparison)",
                      cfg, p_blast, data, "independent_paper",
                      {"dataset_version": f"C-RVDB v31.0 primary dataset, {classes} classes",
                       "split": "350 indexed and 150 queried sequences per class",
                       "population": "6,000 test sequences" if classes == "40" else "4,950 test sequences",
                       "inputs": "Nucleotide sequence up to 2,046 bp",
                       "adaptation": "None: BLAST database built from the training FASTA, max_target_seqs = 1" if "blast" in label
                       else "None: frozen weights, max pooling over all tokens, 1-NN over the indexed training embeddings",
                       "metric_implementation": "Accuracy over test sequences; macro-averaged F1, precision and recall",
                       "aggregation": "Pooled over test sequences (accuracy); macro over classes (F1, precision, recall)"},
                      f"Table 7, row '{classes} classes / {label}'",
                      limitations=["Independent evaluation; the authors develop none of the methods compared."])
    for column, metric, qual in zip([m[0] for m in T7_METRICS], [m[1] for m in T7_METRICS], [m[2] for m in T7_METRICS]):
        printed = cells[[m[0] for m in T7_METRICS].index(column)]
        b.result(f"t7-{classes}-{label}-{column}", ev, metric, printed,
                 f"Table 7, row '{classes} classes / {label}', column '{column}'",
                 qualifier=qual or f"{classes}-class RVDB dataset", method_note=NOTE)

# Table 10: long-sequence dataset.
t10 = table_rows(lines, "Table 10. Classification results on the long-sequence dataset", "4. Discussion")
T10_ROWS = [("DNABERT-2", "DNABERT-2ᵃ", configs[("DNABERT-2", "mean-all")], True),
            ("NTv2-50M", "NTv2-50Mᵃ", configs[("NTv2-50M", "mean-all")], True),
            ("NTv2-250M", "NTv2-250Mᵃ", configs[("NTv2-250M", "mean-all")], True),
            ("NTv3-650M", "NTv3-650M", configs[("NTv3-650M", "max-all")], False),
            ("blastn", "BLAST (blastn)", blastn, False)]
T10_METRICS = [("Accuracy", "accuracy", None), ("Bal. Acc.", "balanced-accuracy", None),
               ("MCC", "matthews-correlation-coefficient", None), ("F1", "macro-f1", None),
               ("Precision", "precision", "macro-averaged over classes"), ("Recall", "recall", "macro-averaged over classes")]
for key, printed_label, cfg, chunked in T10_ROWS:
    row = next(l for l in t10 if l.strip().startswith(printed_label))
    cells = re.findall(r"0\.\d{4}", row)
    assert len(cells) == 6, (key, row)
    ev = b.evaluation(f"t10-{key}", f"{printed_label} on the RVDB long-sequence dataset, 16 classes",
                      cfg, p_long, dlong, "independent_paper",
                      {"dataset_version": "C-RVDB v31.0 long-sequence dataset, 16 classes",
                       "split": "About 4 indexed and about 16 queried sequences per class",
                       "population": "256 test sequences",
                       "inputs": "Whole viral genome, 84,587 to 409,110 bp" + (", scored over overlapping chunks" if chunked else ", processed whole"),
                       "adaptation": "None: BLAST database built from the training FASTA, max_target_seqs = 1" if key == "blastn"
                       else "None: frozen weights, 1-NN over the indexed training embeddings",
                       "metric_implementation": "Accuracy, balanced accuracy, MCC and macro-averaged F1, precision and recall",
                       "aggregation": "Over chunks" if chunked else "Over whole test sequences"},
                      f"Table 10, row '{printed_label}'",
                      limitations=["Independent evaluation; the authors develop none of the methods compared."] +
                      (["Scored over overlapping chunks rather than whole sequences (Table 10 footnote a), so not the same unit as the other rows."] if chunked else []))
    for column, metric, qual in T10_METRICS:
        printed = cells[[m[0] for m in T10_METRICS].index(column)]
        b.result(f"t10-{key}-{column}", ev, metric, printed,
                 f"Table 10, row '{printed_label}', column '{column}'",
                 unit="unitless" if metric == "matthews-correlation-coefficient" else "fraction",
                 qualifier=qual or ("16-class long-sequence RVDB dataset, chunk-scored" if chunked else "16-class long-sequence RVDB dataset"),
                 method_note=NOTE)

counts = b.write(HERE.parent)
print(counts, sum(counts.values()))
