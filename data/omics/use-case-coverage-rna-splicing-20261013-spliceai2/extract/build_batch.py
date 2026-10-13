"""Build the SpliceAI2 (Jaganathan et al. 2026, bioRxiv v1) extraction batch.

Usage: python3 -I build_batch.py <biorxiv-v1.full.pdf> <supplementary-table-1.tsv> <batch-dir>

Reads the pinned bioRxiv v1 PDF with poppler (pdftotext -layout and -bbox), checks the SHA-256 of both
inputs, asserts every printed value it records (row labels, column order and label positions), and writes
batch.jsonl (sorted by id) and claims.csv. All records are written with status needs_review: this is an
extraction, not a review.
"""
import csv, hashlib, html, json, os, re, subprocess, sys

PDF_SHA = "f8f3db2c3943d4827b670bc2e962e0cec8fbe96e0b1acf9d4a9b9f0c7a78c06b"
TSV_SHA = "f46bf8c10880cc2359b6070c1e85af8e5ae7768f75e2580970f6078b54415be7"
PDF_URL = "https://www.biorxiv.org/content/10.64898/2026.10.08.757673v1.full.pdf"
TSV_URL = "https://www.biorxiv.org/content/biorxiv/early/2026/10/11/2026.10.08.757673/DC1/embed/media-1.tsv?download=true"
TODAY = "2026-10-13"
P = "rna-splicing-20261013-spliceai2"
EXTRACTOR = "Extractor: Claude (Opus 5.5) research agent spliceai2-extract; not independent review; no human review claimed"

SRC_ART = P + "-source-article"
SRC_TSV = P + "-source-supplementary-table-1"
SRC_ILL = P + "-source-illumina-pdf"
SRC_README = P + "-source-github-readme"
SRC_LICENCE = P + "-source-github-licence"

pdf, tsv, out = sys.argv[1], sys.argv[2], sys.argv[3]


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


assert sha(pdf) == PDF_SHA, "pinned PDF hash mismatch"
assert sha(tsv) == TSV_SHA, "pinned supplementary table hash mismatch"


def page_text(p):
    return subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-layout", pdf, "-"], check=True,
                          capture_output=True, text=True).stdout


def norm(t):
    return re.sub(r"\s+", " ", t)


# Whitespace-normalised full text with the bioRxiv licence header (printed at the top of every page) removed,
# so that sentences broken across pages can be matched.
HEADER = re.compile(r"bioRxiv preprint doi: https://doi\.org/10\.64898/2026\.10\.08\.757673; this version posted October 11, 2026\. "
                    r"The copyright holder for this preprint \(which was not certified by peer review\) is the author/funder, who has "
                    r"granted bioRxiv a license to display the preprint in perpetuity\. It is made available under a CC-BY-NC 4\.0 "
                    r"International license\. ?")
_full = norm(subprocess.run(["pdftotext", "-layout", pdf, "-"], check=True, capture_output=True, text=True).stdout)
assert len(HEADER.findall(_full)) == 57, "expected the licence header once on each of 57 pages"
FULL = HEADER.sub("", _full)


def must(phrase):
    assert phrase in FULL, "phrase not in pinned text: " + phrase
    return phrase


def words(p):
    """(xMin, yMin, word) for every word on page p, from pdftotext -bbox."""
    xml = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-bbox", pdf, "-"], check=True,
                         capture_output=True, text=True).stdout
    return [(float(a), float(b), html.unescape(w)) for a, b, w in
            re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">([^<]*)</word>', xml)]


def labels_left_to_right(p, expected, ymin, ymax, xmin=0.0):
    """Assert the printed bar labels appear once each in the box and in the given left-to-right order."""
    found = [(x, w) for x, y, w in words(p) if w in expected and ymin <= y <= ymax and x >= xmin]
    assert sorted(w for _, w in found) == sorted(expected), (p, found)
    order = [w for _, w in sorted(found)]
    assert order == expected, (p, order, expected)
    return order


# ---------------------------------------------------------------- printed values
MODELS = ["SpliceAI", "Pangolin", "AlphaGenome", "SpliceAI2"]

# Extended Data Fig. 2, top block (page 52): one row per model, 4 + 4 + 3 + 3 + 3 cells.
ED2_PAGE = 52
ed2 = page_text(ED2_PAGE)
assert "Extended Data Fig. 2 | Model performance comparison and ablation studies." in ed2
head = re.search(r"GTEx GT/AG \(auPRC\)\s+GTEx GT/AG \(ρ\)\s+GTEx sQTL \(auROC\)\s+GTEx sQTL \(ρ\)\s+OpenSplice MPRA \(ρ\)", ed2)
assert head, "Extended Data Fig. 2 panel titles not found in order"
block = ed2[head.end():ed2.index("Usage transformation")]
ED2 = {}
for m in MODELS:
    row = re.search(r"^\s*" + m + r"((?:\s+\d\.\d\d){17})\s*$", block, re.M)
    assert row, "row " + m
    ED2[m] = row.group(1).split()
assert len(ED2) == 4
# Column labels are rotated in the figure; read from the rendered page and checked against the legend text.
assert "including exonic, near intronic, and deep intronic (≥500 bp from nearest exon)" in norm(ed2)
ED2_PANELS = [
    ("gtex-gtag-detection", ["All", "Exon", "Near intronic", "Deep intronic"], "GTEx GT/AG (auPRC)"),
    ("gtex-gtag-usage", ["All", "Exon", "Near intronic", "Deep intronic"], "GTEx GT/AG (ρ)"),
    ("gtex-sqtl-classification", ["All", "Exon", "Intron"], "GTEx sQTL (auROC)"),
    ("gtex-sqtl-effect-size", ["All", "Exon", "Intron"], "GTEx sQTL (ρ)"),
    ("opensplice-mpra", ["All", "Exon", "Intron"], "OpenSplice MPRA (ρ)"),
]
# Fig. 1d prints the same "All" values as bar labels; check they agree.
fig1 = norm(page_text(11))
for m in MODELS:
    for i in (0, 4, 8, 11, 14):
        assert ED2[m][i] in fig1, ("Fig. 1d label", m, ED2[m][i])

# Main-text statements that repeat Extended Data Fig. 2 cells.
must("SpliceAI2 considerably outperformed the next best model, SpliceAI (auPRC, 0.77 versus 0.66)")
must("more accurately than the next best model, Pangolin (Spearman ρ, 0.63 versus 0.47)")
must("(auROC, 0.76 versus 0.73 for AlphaGenome)")
must("(Spearman ρ, 0.73 versus 0.68 for AlphaGenome)")
must("(Spearman ρ, 0.59 versus 0.55 for SpliceAI)")
assert (ED2["SpliceAI2"][0], ED2["SpliceAI"][0]) == ("0.77", "0.66")
assert (ED2["SpliceAI2"][4], ED2["Pangolin"][4]) == ("0.63", "0.47")
assert (ED2["SpliceAI2"][8], ED2["AlphaGenome"][8]) == ("0.76", "0.73")
assert (ED2["SpliceAI2"][11], ED2["AlphaGenome"][11]) == ("0.73", "0.68")
assert (ED2["SpliceAI2"][14], ED2["SpliceAI"][14]) == ("0.59", "0.55")

# Fig. 4g (page 17): bar labels, left to right, in legend order SpliceAI, Pangolin, AlphaGenome, SpliceAI2.
FIG4G = dict(zip(MODELS, labels_left_to_right(17, ["0.48", "0.40", "0.36", "0.59"], 360, 415, xmin=100)))
must("SpliceAI2 also considerably outperformed competing models (auPRC, 0.59 versus 0.48 for SpliceAI)")
# Fig. 3c and 3f (page 15): bar labels, left to right, legend SpliceAI, Pangolin, AlphaGenome, SpliceAI2.
FIG3C = dict(zip(MODELS, labels_left_to_right(15, ["-0.096", "-0.110", "-0.105", "-0.122"], 90, 160, xmin=430)))
FIG3F = dict(zip(MODELS, labels_left_to_right(15, ["-0.463", "-0.475", "-0.481", "-0.504"], 250, 320, xmin=430)))

TXT_AG_SS = must("although the raw splice site score with maximum aggregation performed noticeably better in GTEx GT/AG auPRC (0.63) and GEL GT/AG auPRC (0.45)")
TXT_PRIOR = must("a SpliceAI2 threshold of 0.25 yielded 23 prioritized rare variants, of which 17 showed evidence of the predicted splicing change")
TXT_EXCESS = must("At a fixed odds ratio of 2, SpliceAI2 recovered 133 excess variants, compared with 114 for the next best model.")
TXT_TISSUE = must("Overall, SpliceAI2 predictions correlated with observed tissue-specific splicing differences (Pearson r = 0.44; Fig. 2b)")
TXT_CB = must("cerebellum versus blood (13,770 splice junctions, Pearson r = 0.58)")
TXT_CT = must("cortex versus testis (39,323 splice junctions, Pearson r = 0.51)")
TXT_SF3B1 = must("a weak polypyrimidine tract, and an A-rich branch point (Pearson r = 0.49; Fig. 2d)")
TXT_DM1 = must("predicted and observed MBNL1- associated splicing differences were correlated in held-out genes (mean Pearson r = 0.26)")
TXT_DM1_042 = must("correlations increased between groups with greater differences in disease severity (Pearson r = 0.42; Fig. 2e)")
TXT_BURDEN = must("cryptic splice variants identified by SpliceAI2 contributing an additional 15%")
TXT_TOPTX = must("SpliceAI2 perfectly reconstructed the most abundant transcript for 82% of held-out genes, compared with 78% when trained without using long-read RNA-seq data")
TXT_SPLIT = must("Genes on human chromosomes 21 and 22 were held out for validation, and all remaining genes were used for training.")
TXT_TRAIN = must("We trained SpliceAI2 end-to-end on splice site and splice junction usage from 314,745 RNA-seq samples spanning human and nine additional mammalian species, together with transcript usage from 330 long-read RNA-seq samples in human and mouse")
TXT_AG_OX = must("All AlphaGenome analyses were conducted at the University of Oxford.")
TXT_OS = must("using SpliceAI, Pangolin, and AlphaGenome scores released with the OpenSplice dataset")
TXT_8EVAL = must("Among 40 scoring configurations tested, the raw composite score with maximum aggregation showed the strongest average performance across the eight evaluations")
for t in ["0.37", "0.38", "0.43", "0.44", "0.5393", "0.5395"]:
    assert t in norm(page_text(55)), ("Extended Data Fig. 4 label", t)

# Supplementary Table 1 totals.
rows = list(csv.reader(open(tsv, newline=""), delimiter="\t"))
assert rows[0] == ["Species", "Common_name", "Reference_genome_assembly", "Data_source", "Number_of_samples", "Number_of_junctions"]
assert len(rows) == 12 and rows[-1][0] == "Total" and rows[-1][4:] == ["314745", "67493026"]
assert sum(int(r[4]) for r in rows[1:-1]) == 314745 and sum(int(r[5]) for r in rows[1:-1]) == 67493026
assert rows[1][:4] == ["Homo_sapiens", "Human", "GRCh38", "recount3 (GTEx, TCGA, CCLE and other SRA-derived projects)"]

# ---------------------------------------------------------------- record helpers
records, claim_rows = [], []
DNA = ["dna-genomes"]
DNA_RNA = ["dna-genomes", "rna-transcriptomes"]


def add(r):
    assert r["id"] not in {x["id"] for x in records}, r["id"]
    records.append(r)
    return r["id"]


def facets(areas, contexts, method_types=None):
    f = {"areas": areas, "contexts": contexts}
    if method_types:
        f["method_types"] = method_types
    return f


def review(method, method_note, sha256=PDF_SHA, url=PDF_URL):
    return {"method": method, "reviewer": ["claude"], "reviewer_note": EXTRACTOR, "date": TODAY,
            "artifact_sha256": sha256, "retrieval_url": url, "method_note": method_note,
            "note": "Extraction only; pending independent review."}


def source(id, name, attrs, areas=DNA_RNA):
    add({"id": id, "kind": "source", "name": name,
         "description": "Primary source retrieved and hashed for the 2026-10-13 SpliceAI2 extraction (issue #127).",
         "status": "needs_review", "facets": facets(areas, ["research"]), "source_ids": [], "links": [], "attributes": attrs})


def entity(kind, id, name, description, attrs, areas, contexts, links=(), method_types=None, sources=(SRC_ART,)):
    return add({"id": id, "kind": kind, "name": name, "description": description, "status": "needs_review",
                "facets": facets(areas, contexts, method_types), "source_ids": list(sources), "links": list(links),
                "attributes": attrs})


def claim(id, name, subject, field, value, locator, sources=(SRC_ART,), sha256=PDF_SHA, url=PDF_URL,
          method=("pdf-text-parse",), note="Statement transcribed from the pinned text layer (pdftotext -layout) and asserted by extract/build_batch.py."):
    add({"id": id, "kind": "claim", "name": name, "description": value, "status": "needs_review", "facets": {},
         "source_ids": list(sources), "links": [{"relation": "subject", "target_id": subject}],
         "attributes": {"field": field, "value": value, "source_locator": locator,
                        "review": review(list(method), note, sha256, url)}})
    claim_rows.append([id, sources[0], locator, value, "claim"])


# ---------------------------------------------------------------- sources
source(SRC_ART, "A unified framework for quantitative splicing and transcript prediction (Jaganathan et al., bioRxiv 2026)", {
    "url": "https://doi.org/10.64898/2026.10.08.757673",
    "artifact_url": PDF_URL,
    "version": "bioRxiv preprint version 1, posted 2026-10-11; full-text PDF (57 pages)",
    "retrieved_at": "2026-10-13T12:40:34Z",
    "artifact_sha256": PDF_SHA,
    "doi": "10.64898/2026.10.08.757673",
    "publication_status": "preprint",
    "licence": "CC-BY-NC-4.0",
    "media_type": "application/pdf",
    "source_locator": "Main text, Methods, Figs. 1 to 4 and Extended Data Figs. 1 to 5",
    "limitations": [
        "Preprint, not peer reviewed. No journal version was found on 2026-10-13 (bioRxiv 'published' field NA).",
        "The paper prints no numbered tables. Model comparisons are printed as numeric labels in Extended Data Fig. 2 (a labelled heatmap) and as bar labels in Figs. 1d, 3c, 3f and 4g; these labels are extracted, unlabelled figure values are not.",
        "All evaluations are by the developers (Illumina employees), with AlphaGenome scored by co-authors at the University of Oxford. Nothing here is independent of the SpliceAI2 authors.",
        "The bioRxiv JATS XML (SHA-256 b15a42024ef755cfab08d2f7e678957e5ac8a4efb63a61c7315b826f8bd69138) holds front matter only, so the PDF is the pinned full text.",
    ],
})
source(SRC_TSV, "Supplementary Table 1: training RNA-seq samples and junctions per species (Jaganathan et al., bioRxiv 2026)", {
    "url": TSV_URL,
    "version": "bioRxiv version 1 supplement DC1 (757673_file02.tsv)",
    "retrieved_at": "2026-10-13T12:40:34Z",
    "artifact_sha256": TSV_SHA,
    "doi": "10.64898/2026.10.08.757673",
    "publication_status": "preprint",
    "licence": "CC-BY-NC-4.0",
    "media_type": "text/tab-separated-values",
    "source_locator": "All 11 data rows (10 species and the Total row)",
})
source(SRC_ILL, "SpliceAI2 manuscript PDF hosted by Illumina", {
    "url": "https://assets.illumina.com/content/dam/illumina-marketing/images/genomics-research/articles/spliceai2/SpliceAI2.pdf",
    "version": "Illumina-hosted manuscript PDF, HTTP Last-Modified 2026-10-08T12:39:35Z; mutable location, the hash describes one retrieval",
    "retrieved_at": "2026-10-13T12:38:36Z",
    "artifact_sha256": "2a264f98acb30e9598a5525461080b9b2891f112ea48f2fb2f8129e605a93be9",
    "publication_status": "official_project_source",
    "media_type": "application/pdf",
    "limitations": [
        "Same 57-page manuscript as the bioRxiv v1 PDF: the word content of the two text layers matches except for the bioRxiv licence header on each page and the reading order of a few rotated figure labels. Values are extracted from the bioRxiv PDF, which has a DOI and a licence.",
    ],
    "missing_metadata": {"licence": {"reason": "unreported", "note": "The PDF prints no licence."}},
})
source(SRC_README, "SpliceAI2 README at commit 1dcd2a1 (Illumina/SpliceAI2)", {
    "url": "https://github.com/Illumina/SpliceAI2/blob/1dcd2a1882a8223095e7529982ae70bcb658340a/README.md",
    "artifact_url": "https://raw.githubusercontent.com/Illumina/SpliceAI2/1dcd2a1882a8223095e7529982ae70bcb658340a/README.md",
    "version": "Commit 1dcd2a1882a8223095e7529982ae70bcb658340a (main, 2026-10-11); two README-only commits after tag v2.0 (aa634374bc8700414b1a5388729faed7c4f7ba07)",
    "retrieved_at": "2026-10-13T12:41:22Z",
    "artifact_sha256": "7973d1c0620d40ee954d3434b645018dcdfffca3c6649b1c69169df745a4a433",
    "publication_status": "official_project_source",
    "licence": "SpliceAI2 Model Terms of Use (LICENSE file in the same repository)",
    "media_type": "text/markdown",
}, areas=DNA)
source(SRC_LICENCE, "SpliceAI2 Model Terms of Use (LICENSE at commit 1dcd2a1, Illumina/SpliceAI2)", {
    "url": "https://github.com/Illumina/SpliceAI2/blob/1dcd2a1882a8223095e7529982ae70bcb658340a/LICENSE",
    "artifact_url": "https://raw.githubusercontent.com/Illumina/SpliceAI2/1dcd2a1882a8223095e7529982ae70bcb658340a/LICENSE",
    "version": "Commit 1dcd2a1882a8223095e7529982ae70bcb658340a; file unchanged since tag v2.0",
    "retrieved_at": "2026-10-13T12:41:22Z",
    "artifact_sha256": "70298b77bd30d2ddfbe01d67b100363599b0b98ccb920e859abcf2a9d15a9c36",
    "publication_status": "official_project_source",
    "licence": "SpliceAI2 Model Terms of Use (proprietary, non-commercial organisations only)",
    "media_type": "text/plain",
}, areas=DNA)

# ---------------------------------------------------------------- model and configurations
MODEL = P + "-model-spliceai2"
entity("model", MODEL, "SpliceAI2",
       "Deep learning model that predicts splice site usage, splice junction usage and complete transcripts from about 200 kb of genomic sequence, and scores variant effects on splicing.",
       {"reported_name": "SpliceAI2", "entity_level": "family",
        "training_data": "Splice site and junction usage from 314,745 short-read RNA-seq samples (67,493,026 junctions) in ten mammalian species, human and mouse from recount3, plus transcript usage from 330 ENCODE long-read samples (189 human, 141 mouse). Human genes on chromosomes 21 and 22 held out for validation.",
        "licence": "SpliceAI2 Model Terms of Use: non-commercial organisations only; research use only, not for diagnostic procedures",
        "access": "Source code on GitHub (Illumina/SpliceAI2, tag v2.0); weights and precomputed scores on Hugging Face (illumina-ai/SpliceAI2) behind a gated licence acceptance; precomputed scores also through DRAGEN Annotation (README)",
        "source_locator": "bioRxiv v1: Main 'Hierarchical model of RNA splicing'; Methods 'Training datasets' and 'SpliceAI2 model'; README 'SpliceAI2'; LICENSE sections 2, 3 and 13",
        "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the evaluated setup is on each configuration"}}},
       DNA, ["research"], method_types=["supervised_machine_learning"], sources=(SRC_ART, SRC_TSV, SRC_README, SRC_LICENCE))

CONFIGS = {}


def config(key, name, model, attrs, sources=(SRC_ART,)):
    id = P + "-config-" + key
    a = {"foundation_model_eligible": False}
    a.update(attrs)
    entity("configuration", id, name, name + ", as evaluated in the SpliceAI2 paper.", a, DNA, ["research"],
           links=[{"relation": "configuration_of", "target_id": model}], method_types=["supervised_machine_learning"], sources=sources)
    CONFIGS[key] = id
    return id


TRAIN_OVERLAP = ("Trained on all human genes except those on chromosomes 21 and 22 (held out for validation). The variant "
                 "benchmarks are genome-wide, so most benchmark variants lie in genes seen in training. Supplementary Table 1 "
                 "lists GTEx among the recount3 human training sources; the paper does not say whether junctions observed in "
                 "the GTEx benchmark samples were removed from training.")
config("spliceai2-ensemble", "SpliceAI2 two-model multispecies ensemble (Jaganathan et al. 2026)", MODEL, {
    "reported_name": "SpliceAI2",
    "version": "Two models trained with identical settings and averaged (bioRxiv v1 Methods); code release v2.0",
    "parameters": "196,608 bp sense-strand input with species one-hot; about 13 million trainable parameters per model; donor, acceptor and junction usage; shared candidate splice sites for both alleles and both models; summary score is the maximum of donor gain, donor loss, acceptor gain and acceptor loss deltas",
    "training_overlap": TRAIN_OVERLAP,
    "access_reuse": "Code at Illumina/SpliceAI2 under the SpliceAI2 Model Terms of Use (non-commercial organisations only; research use only). Weights on Hugging Face illumina-ai/SpliceAI2, gated.",
    "code_commit": "1dcd2a1882a8223095e7529982ae70bcb658340a",
    "source_locator": "Methods 'SpliceAI2 model' (Training, Variant effect prediction); README; LICENSE",
    "missing_metadata": {"checkpoint": {"reason": "unreported", "note": "The paper does not say whether the evaluated ensemble is the released Hugging Face checkpoints (spliceai2_multispecies_13M_01 and _02)."}},
}, sources=(SRC_ART, SRC_README, SRC_LICENCE))
config("spliceai2-tissue-147rbp", "SpliceAI2 tissue-specific fine-tune with a 147-RBP expression signature, 48 GTEx v8 tissues (Jaganathan et al. 2026)", MODEL, {
    "reported_name": "SpliceAI2 (tissue-specific)",
    "version": "Fine-tuned from the pretrained multispecies SpliceAI2; two replicates averaged",
    "parameters": "Signature injection (bi-FiLM) before each of 20 MetaFormer blocks and a three-layer cross-attention decoder; 147 RBP expression values per tissue (TMM, log2 CPM, divided by 20); 1 kb flanks, input capped at 64 kb; 10 epochs",
    "training_overlap": "Fine-tuned on chromosomes 2, 4, 6, 8, 10 to 22 and X; chromosomes 1, 3, 5, 7 and 9 used for validation and evaluation. The pretrained encoder saw all human genes except chromosomes 21 and 22.",
    "source_locator": "Methods 'Tissue-specific model architecture and fine-tuning'; Extended Data Fig. 3",
    "missing_metadata": {"checkpoint": {"reason": "unreported", "note": "No released tissue-specific weights are named in the paper or README."}},
})
config("spliceai2-sf3b1-uvm", "SpliceAI2 fine-tuned on SF3B1-mutant and wild-type uveal melanoma (Jaganathan et al. 2026)", MODEL, {
    "reported_name": "SpliceAI2 (SF3B1)",
    "version": "Tissue-specific framework fine-tuned on TCGA uveal melanoma RNA-seq",
    "parameters": "Mutant and wild-type conditions supplied as two 147-RBP expression vectors with identical DNA input; 18 SF3B1-mutant and 62 wild-type tumours",
    "source_locator": "Main 'Modeling tissue-specific splicing' paragraph 4; Methods 'SF3B1-mutant uveal melanoma (UVM)'",
    "missing_metadata": {"checkpoint": {"reason": "unreported", "note": "No released weights named."}},
})
config("spliceai2-dm1", "SpliceAI2 fine-tuned on myotonic dystrophy type 1 muscle RNA-seq (Jaganathan et al. 2026)", MODEL, {
    "reported_name": "SpliceAI2 (myotonic dystrophy)",
    "version": "Tissue-specific framework fine-tuned on GSE86356 tibialis anterior RNA-seq",
    "parameters": "Four 147-RBP signatures (healthy and low, medium and high disease severity), with inferred free MBNL1 expression 9.17, 6.01, 3.67 and 1.32 log2 TMM CPM (n = 11, 15, 14 and 15)",
    "source_locator": "Main 'Modeling tissue-specific splicing' paragraph 4; Methods 'MBNL1-depleted myotonic dystrophy'",
    "missing_metadata": {"checkpoint": {"reason": "unreported", "note": "No released weights named."}},
})
config("spliceai-position-resolved", "SpliceAI 1.3.1, position-resolved delta at the effect position, masking off (Jaganathan et al. 2026)", "catalog-model-spliceai", {
    "reported_name": "SpliceAI",
    "version": "1.3.1, modified by the authors to report position-resolved donor and acceptor predictions for both alleles",
    "parameters": "Five bundled models averaged; GRCh38; masking disabled; donor or acceptor channel chosen by effect type; signed delta (alternative minus reference) at the effect position. Used for the GTEx and GEL GT/AG, GTEx sQTL and UK Biobank benchmarks.",
    "source_locator": "Methods 'Evaluation of competing methods', SpliceAI paragraph",
})
config("spliceai-standard", "SpliceAI 1.3.1 standard delta scores, masking off (Jaganathan et al. 2026)", "catalog-model-spliceai", {
    "reported_name": "SpliceAI",
    "version": "1.3.1",
    "parameters": "Standard SpliceAI scores with default settings and masking disabled. Used for the population genetic and GEL rare-disease analyses.",
    "source_locator": "Methods 'Evaluation of competing methods', SpliceAI paragraph",
})
config("pangolin-position-resolved", "Pangolin, per-position score at the effect position, masking off (Jaganathan et al. 2026)", "catalog-model-pangolin", {
    "reported_name": "Pangolin",
    "parameters": "Locally modified build with the released weights and architecture unchanged, allowing scoring on soft-masked sequence; GRCh38; output score cutoff 0; per-position prediction at the effect position; masking off. Used for the GTEx and GEL GT/AG, GTEx sQTL and UK Biobank benchmarks.",
    "source_locator": "Methods 'Evaluation of competing methods', Pangolin paragraph",
    "missing_metadata": {"version": {"reason": "unreported", "note": "Pangolin release not printed."}},
})
config("pangolin-standard", "Pangolin default settings, maximum absolute gain or loss score, masking off (Jaganathan et al. 2026)", "catalog-model-pangolin", {
    "reported_name": "Pangolin",
    "parameters": "Default settings, masking disabled; reported value is the maximum absolute score across the gain and loss channels. Used for the population genetic and GEL rare-disease analyses.",
    "source_locator": "Methods 'Evaluation of competing methods', Pangolin paragraph",
    "missing_metadata": {"version": {"reason": "unreported", "note": "Pangolin release not printed."}},
})
config("alphagenome-composite-max", "AlphaGenome raw composite splice score, maximum aggregation (Jaganathan et al. 2026)", "catalog-model-alphagenome", {
    "reported_name": "AlphaGenome",
    "parameters": "1 Mb sequence context centred on the variant; SPLICE_SITES, SPLICE_SITE_USAGE and SPLICE_JUNCTIONS scorers via score_variant() and predict_variant(); composite = splice site + splice site usage + one fifth of splice junction effect; raw outputs, maximum aggregation; chosen from 40 scoring configurations as best on average across eight evaluations",
    "access_reuse": "Run at the University of Oxford by co-authors (Y.K., E.M.W.; supervised by S.J.S.)",
    "source_locator": "Methods 'Evaluation of competing methods', AlphaGenome paragraph; Author contributions",
    "missing_metadata": {"version": {"reason": "unreported", "note": "API or weights version not printed."}},
})
config("alphagenome-splice-site-max", "AlphaGenome raw splice site score, maximum aggregation (Jaganathan et al. 2026)", "catalog-model-alphagenome", {
    "reported_name": "AlphaGenome (raw splice site score)",
    "parameters": "1 Mb context; raw SPLICE_SITES score with maximum aggregation; one of the 40 scoring configurations tested, reported in the Methods only for GTEx and GEL GT/AG auPRC",
    "access_reuse": "Run at the University of Oxford by co-authors",
    "source_locator": "Methods 'Evaluation of competing methods', AlphaGenome paragraph",
    "missing_metadata": {"version": {"reason": "unreported", "note": "API or weights version not printed."}},
})
for key, model, label in [("spliceai-opensplice-released", "catalog-model-spliceai", "SpliceAI"),
                          ("pangolin-opensplice-released", "catalog-model-pangolin", "Pangolin"),
                          ("alphagenome-opensplice-released", "catalog-model-alphagenome", "AlphaGenome")]:
    config(key, label + " scores released with the OpenSplice dataset (Jaganathan et al. 2026)", model, {
        "reported_name": label,
        "parameters": "Exon-skipping predictions released with the OpenSplice MPRA dataset (reference 23); this paper did not rescore them and does not describe their settings",
        "source_locator": "Methods 'Variant effect benchmarks', OpenSplice MPRA paragraph",
        "missing_metadata": {"version": {"reason": "unreported", "note": "Settings are those of the OpenSplice release, not printed in this paper."}},
    })

# ---------------------------------------------------------------- datasets
D = {}


def dataset(key, name, description, attrs, areas=DNA_RNA, contexts=("research",)):
    id = P + "-data-" + key
    entity("dataset", id, name, description, attrs, areas, list(contexts))
    D[key] = id


GTEX_ACCESS = "Controlled access: GTEx individual-level WGS and RNA-seq through dbGaP phs000424.v9.p2. The derived benchmark variant lists are not released with the paper (Data and code availability names only code, weights and precomputed scores)."
GEL_ACCESS = "Controlled access: Genomics England National Genomic Research Library (project ID 754), only inside the Genomics England Research Environment, for approved Genomics England Research Network members under participant-led governance. Benchmark variant lists are not released."
dataset("gtex-gtag", "GTEx rare GT/AG-creating SNVs with RNA-seq cryptic splicing labels (Jaganathan et al. 2026)",
        "Rare SNVs in GTEx WGS that create a GT or AG dinucleotide, labelled cryptic gains when matched RNA-seq shows a novel junction at the site only in carriers (and in more than one sample), or null when the gene is highly expressed, the variant is carried by at least ten individuals and no junction is seen.",
        {"version": "GTEx WGS and matched RNA-seq (dbGaP phs000424.v9.p2), as processed by the authors",
         "population": "4,545 cryptic splice variants and 573,967 null variants; essential splice variants excluded",
         "positives": 4545, "negatives": 573967,
         "assay": "Short-read RNA-seq junctions from STAR alignments to a personalised diploid genome, reads from the variant-carrying haplotype",
         "split": "No split; scored with pretrained models",
         "reuse_restrictions": GTEX_ACCESS,
         "source_locator": "Main 'Hierarchical model of RNA splicing' paragraph 3; Methods 'Variant effect benchmarks' (GTEx and GEL GT/AG); Fig. 1d; Acknowledgements"})
dataset("gtex-sqtl", "GTEx v8 sQTL fine-mapped and null SNVs near junction ends (Jaganathan et al. 2026)",
        "GTEx v8 significant sQTL variant-junction pairs, restricted to SNVs within 50 bp of either junction end; fine-mapped if PIP >= 0.9 in at least one tissue, null if PIP < 0.1 in all tissues and absolute mean effect size below 0.5.",
        {"version": "GTEx v8 significant sQTL pairs and SuSiE fine-mapping results (references 51 and 52)",
         "population": "2,385 fine-mapped and 3,824 null variants after excluding essential splice dinucleotides; effect sizes averaged across tissues with a significant association",
         "positives": 2385, "negatives": 3824,
         "split": "No split; scored with pretrained models",
         "source_locator": "Methods 'Variant effect benchmarks', GTEx sQTL paragraph; Fig. 1d",
         "missing_metadata": {"reuse_restrictions": {"reason": "unreported", "note": "Access terms for the downloaded sQTL and fine-mapping files are not stated."}}})
dataset("opensplice-mpra", "OpenSplice MPRA single-nucleotide substitutions with measured delta PSI (as used by Jaganathan et al. 2026)",
        "Massively parallel reporter assay measuring the effect of single-nucleotide substitutions on inclusion of human exons (OpenSplice, reference 23: bioRxiv doi 10.64898/2026.05.22.727141).",
        {"version": "OpenSplice dataset release used by the authors (version not printed)",
         "population": "283,121 single-nucleotide substitutions across 599 exons with a measured delta PSI",
         "variants": 283121,
         "assay": "Reporter assay exon inclusion (delta PSI)",
         "split": "No split; scored with pretrained models",
         "source_locator": "Methods 'Variant effect benchmarks', OpenSplice MPRA paragraph; reference 23; Fig. 1d",
         "missing_metadata": {"reuse_restrictions": {"reason": "unreported", "note": "Not stated in this paper; see the OpenSplice preprint."}}},
        areas=DNA_RNA)
dataset("gel-rnaseq", "Genomics England rare-disease participants with WGS and blood RNA-seq (Jaganathan et al. 2026)",
        "Rare-disease probands from the Genomics England 100,000 Genomes Project with matched WGS and blood RNA-seq, used to label cryptic splice gains for rare GT/AG-creating variants and to check predicted splicing changes.",
        {"version": "Genomics England NGRL rare-disease RNA-seq (SJ.out.tab junction counts) and aggV2 variant calls, as accessed under project 754",
         "population": "5,435 probands with matched WGS and RNA-seq; GT/AG benchmark of 3,065 cryptic and 1,775,800 null variants; 292,651 variants with SpliceAI2 > 0.1, of which 41,959 variant-gene pairs had a qualifying junction",
         "patient_count": 5435, "positives": 3065, "negatives": 1775800,
         "assay": "Blood short-read RNA-seq (Results paragraph 'We next leveraged blood RNA-seq data'); junctions from personalised diploid-genome alignments for GT/AG variants and cohort percentile of anchor usage for others",
         "split": "No split; scored with pretrained models",
         "reuse_restrictions": GEL_ACCESS,
         "source_locator": "Main 'Contribution to rare genetic disease' paragraph 4; Methods 'RNA-seq validation' and 'Variant effect benchmarks'; Fig. 4g; Data and code availability"},
        contexts=("clinical_research",))
dataset("gel-100kgp-dominant", "Genomics England 100,000 Genomes Project probands with dominant-disorder panels (Jaganathan et al. 2026)",
        "Rare-disease probands whose PanelApp panels have fewer than 100 confirmed or probable genes, restricted to dominant panel genes, excluding genes with a reported TIER1 variant; singleton rare SNVs and indels.",
        {"version": "Genomics England NGRL (project 754); PanelApp accessed 25 April 2023; GEL v16 TIER1 exclusions",
         "population": "8,778 probands with panels under 100 genes; 7,504 probands with dominant panel genes",
         "probands": 7504,
         "split": "No split; ten phenotype-shuffled datasets as background",
         "reuse_restrictions": GEL_ACCESS,
         "source_locator": "Methods 'Genomics England rare disease analysis', 'Panel-matched disease gene enrichment'"},
        areas=DNA, contexts=("clinical_research",))
dataset("population-constraint", "gnomAD, TOPMed and UK Biobank splice-proximal SNV depletion set (Jaganathan et al. 2026)",
        "Protein-coding SNVs within 30 bp of annotated splice sites: simulated absent variants against observed common variants (allele frequency >= 0.01%), trinucleotide-matched about 1:1; essential splice variants excluded.",
        {"version": "gnomAD v3.1.2, TOPMed freeze 8 and UK Biobank (~450k) combined",
         "population": "More than 627,000 individuals with WGS; Fig. 3c restricted to high-pLI genes",
         "split": "No split",
         "reuse_restrictions": "UK Biobank under Resource Application 33751 (controlled); gnomAD and TOPMed access terms not stated in the paper",
         "source_locator": "Main 'Functional effects in human populations' paragraph 1; Methods 'Population genetics analysis'; Acknowledgements"},
        areas=DNA)
dataset("ukb-proteomics", "UK Biobank rare splice-region variants with carrier plasma protein levels (Jaganathan et al. 2026)",
        "Rare (allele frequency <= 0.1%) VEP splice-region variants carried by at least two individuals with Olink plasma protein measurements, in 1,656 genes with burden associations; essential splice variants excluded.",
        {"version": "UK Biobank WGS (~500,000) and plasma proteomics (Olink) residuals, unrelated European-ancestry carriers",
         "population": "6,149 rare splice-region variants in 1,656 genes; 36,764 participants with WGS and plasma proteomics",
         "variants": 6149,
         "split": "No split",
         "reuse_restrictions": "Controlled access: UK Biobank Resource Application 33751",
         "source_locator": "Main 'Functional effects in human populations' paragraph 2; Methods 'UK Biobank proteomics analysis'; Fig. 3d"},
        areas=DNA)
dataset("gtex-tissue-junctions", "GTEx v8 tissue-specific junction usage differences on held-out chromosomes (Jaganathan et al. 2026)",
        "Anchor-based junction usage from GTEx v8 junction counts summed per tissue, for protein-coding genes (GENCODE v48) on chromosomes 1, 3, 5, 7 and 9; for each junction the 24 highest-usage tissues are paired with the 24 lowest.",
        {"version": "GTEx v8 short-read junction counts, 48 tissues",
         "population": "14,712,948 junction-tissue-pair comparisons across all tissue pairs; cerebellum versus blood 13,770 and cortex versus testis 39,323 junctions",
         "split": "Held-out chromosomes 1, 3, 5, 7 and 9",
         "reuse_restrictions": GTEX_ACCESS,
         "source_locator": "Main 'Modeling tissue-specific splicing' paragraph 2; Methods 'Prediction of tissue-specific junction usage'; Fig. 2b"},
        areas=["rna-transcriptomes"])
dataset("tcga-uvm", "TCGA uveal melanoma RNA-seq, SF3B1-mutant and wild-type (as used by Jaganathan et al. 2026)",
        "Mutation data, expression and junction counts from 80 uveal melanoma samples from the Genomic Data Commons.",
        {"version": "Genomic Data Commons TCGA-UVM, as downloaded by the authors (release not printed)",
         "population": "80 samples: 18 SF3B1-mutant and 62 wild-type tumours; junctions with more than 500 anchor reads in held-out genes",
         "split": "Held-out genes",
         "source_locator": "Methods 'SF3B1-mutant uveal melanoma (UVM)'; Main 'Modeling tissue-specific splicing' paragraph 4",
         "missing_metadata": {"reuse_restrictions": {"reason": "unreported", "note": "Access terms not stated in the paper."}}},
        areas=["rna-transcriptomes"])
dataset("dm1-gse86356", "Myotonic dystrophy type 1 tibialis anterior RNA-seq, GEO GSE86356 (as used by Jaganathan et al. 2026)",
        "Published RNA-seq of 55 tibialis anterior biopsies from 44 individuals with myotonic dystrophy type 1 and 11 unaffected individuals, grouped by inferred MBNL activity.",
        {"version": "GEO GSE86356, processed with the GTEx RNA-seq pipeline V10 (GRCh38, GENCODE v39)",
         "population": "55 biopsies; healthy n = 11 and low, medium and high severity n = 15, 14 and 15",
         "accession": "GSE86356",
         "split": "Held-out genes",
         "source_locator": "Methods 'MBNL1-depleted myotonic dystrophy'",
         "missing_metadata": {"reuse_restrictions": {"reason": "unreported", "note": "Not stated in the paper."}}},
        areas=["rna-transcriptomes"])

# ---------------------------------------------------------------- protocols
PR = {}
COMMON_LIMITS = [
    "Developer-reported: the SpliceAI2 authors (Illumina) built the benchmark, chose comparator settings and ran every model; AlphaGenome was scored by co-authors at the University of Oxford.",
    "Training overlap: SpliceAI2 was trained on all human genes except those on chromosomes 21 and 22, and the benchmark is genome-wide, so most variants lie in genes seen in training. Supplementary Table 1 lists GTEx among the recount3 human training sources.",
    "Essential splice variants are excluded, so results do not cover canonical GT/AG disruption.",
    "No confidence intervals or resampling uncertainty are printed.",
    "Preprint (bioRxiv v1), not peer reviewed.",
]


def protocol(key, name, description, attrs, data_key, areas=DNA, contexts=("research",), extra_limits=()):
    id = P + "-protocol-" + key
    a = dict(attrs)
    a["limitations"] = list(extra_limits) + COMMON_LIMITS
    entity("protocol", id, name, description, a, areas, list(contexts),
           links=[{"relation": "uses_data", "target_id": D[data_key]}])
    PR[key] = id
    return id


protocol("gtex-gtag-detection", "Cryptic splice site activation by rare GT/AG-creating SNVs, GTEx WGS and RNA-seq (SpliceAI2 paper, auPRC)",
         "Separate 4,545 RNA-seq-confirmed cryptic splice gains from 573,967 null GT/AG-creating variants by model score.",
         {"protocol": "Score every rare GT/AG-creating SNV with each model at the created site; compute auPRC for cryptic gains against nulls, overall and by region (exonic, near intronic, deep intronic >= 500 bp from the nearest exon).",
          "version": "bioRxiv v1 Extended Data Fig. 2 and Fig. 1d", "metric": "auprc", "metric_direction": "higher",
          "source_locator": "Methods 'Variant effect benchmarks' (GTEx and GEL GT/AG); Extended Data Fig. 2 panel 'GTEx GT/AG (auPRC)'; Fig. 1d"},
         "gtex-gtag", areas=DNA_RNA,
         extra_limits=["Null variants require at least ten carriers and high gene expression, so the class balance (4,545 of 578,512) and auPRC depend on those filters.",
                       "Region stratum sizes are not printed."])
protocol("gtex-gtag-usage", "Cryptic splice site usage among RNA-seq-confirmed GT/AG-creating SNVs, GTEx (SpliceAI2 paper, Spearman)",
         "Rank correlation between predicted and observed cryptic splice site usage for the 4,545 cryptic gains.",
         {"protocol": "For each cryptic gain, observed usage is the novel junction count divided by the summed counts at the gene's most abundant donor or acceptor; Spearman correlation with model scores, overall and by region.",
          "version": "bioRxiv v1 Extended Data Fig. 2 and Fig. 1d", "metric": "spearman-correlation", "metric_direction": "higher",
          "source_locator": "Methods 'Variant effect benchmarks' (GTEx and GEL GT/AG, last sentence); Extended Data Fig. 2 panel 'GTEx GT/AG (ρ)'"},
         "gtex-gtag", areas=DNA_RNA, extra_limits=["Region stratum sizes are not printed."])
protocol("gtex-sqtl-classification", "GTEx v8 fine-mapped sQTL SNVs against non-prioritised SNVs near junction ends (SpliceAI2 paper, auROC)",
         "Separate 2,385 fine-mapped sQTL variants (PIP >= 0.9) from 3,824 null variants (PIP < 0.1 everywhere) by model score.",
         {"protocol": "Score SNVs within 50 bp of the associated junction ends; auROC for fine-mapped against null, overall and by exonic or intronic position.",
          "version": "bioRxiv v1 Extended Data Fig. 2 and Fig. 1d", "metric": "auroc", "metric_direction": "higher",
          "source_locator": "Methods 'Variant effect benchmarks', GTEx sQTL paragraph; Extended Data Fig. 2 panel 'GTEx sQTL (auROC)'"},
         "gtex-sqtl", extra_limits=["Exon and intron stratum sizes are not printed."])
protocol("gtex-sqtl-effect-size", "GTEx v8 fine-mapped sQTL effect size prediction (SpliceAI2 paper, Spearman)",
         "Rank correlation between model scores and tissue-averaged sQTL effect sizes for 2,385 fine-mapped variants.",
         {"protocol": "Spearman correlation between model score and the sQTL effect size averaged across tissues with a significant association, overall and by exonic or intronic position.",
          "version": "bioRxiv v1 Extended Data Fig. 2 and Fig. 1d", "metric": "spearman-correlation", "metric_direction": "higher",
          "source_locator": "Methods 'Variant effect benchmarks', GTEx sQTL paragraph; Extended Data Fig. 2 panel 'GTEx sQTL (ρ)'"},
         "gtex-sqtl", extra_limits=["Exon and intron stratum sizes are not printed."])
protocol("opensplice-mpra", "OpenSplice MPRA delta PSI prediction for 283,121 single-nucleotide substitutions in 599 exons (SpliceAI2 paper, Spearman)",
         "Rank correlation between predicted and measured exon-inclusion change in the OpenSplice reporter assay.",
         {"protocol": "SpliceAI2 effect = mean of the donor usage change at the downstream donor and the acceptor usage change at the upstream acceptor of the measured exon; SpliceAI, Pangolin and AlphaGenome use the scores released with OpenSplice. Spearman against measured delta PSI, overall and by exonic or intronic position.",
          "version": "bioRxiv v1 Extended Data Fig. 2 and Fig. 1d", "metric": "spearman-correlation", "metric_direction": "higher",
          "source_locator": "Methods 'Variant effect benchmarks', OpenSplice MPRA paragraph; Extended Data Fig. 2 panel 'OpenSplice MPRA (ρ)'"},
         "opensplice-mpra", areas=DNA_RNA,
         extra_limits=["Comparator scores are those released with OpenSplice, not rescored by the authors, while SpliceAI2 was scored by its developers with an exon-skipping formula; settings therefore differ between systems.",
                       "The Methods also say the AlphaGenome configuration was chosen across 'eight evaluations', which may include this benchmark; the paper does not reconcile this with the use of released OpenSplice scores.",
                       "Reporter exon inclusion in a minigene context, not endogenous or patient splicing."])
protocol("gel-gtag-detection", "Cryptic splice site activation by rare GT/AG-creating variants in Genomics England blood RNA-seq (SpliceAI2 paper, auPRC)",
         "Separate 3,065 RNA-seq-confirmed cryptic gains from 1,775,800 null GT/AG-creating variants in 5,435 rare-disease participants with WGS and blood RNA-seq.",
         {"protocol": "Same labelling pipeline as the GTEx GT/AG benchmark applied to Genomics England samples (novel junction only in carriers, from personalised diploid-genome alignments); auPRC of each model's score at the created site.",
          "version": "bioRxiv v1 Fig. 4g", "metric": "auprc", "metric_direction": "higher",
          "source_locator": "Main 'Contribution to rare genetic disease' paragraph 4; Methods 'Variant effect benchmarks' (GTEx and GEL GT/AG); Fig. 4g"},
         "gel-rnaseq", areas=DNA_RNA, contexts=("clinical_research",),
         extra_limits=["Blood RNA-seq only: splicing changes in genes not expressed in blood are not observable, so nulls can include variants that splice in other tissues.",
                       "The GTEx rule that a cryptic gain is seen in more than one sample applies to GTEx only; the paper does not state a replacement rule for Genomics England.",
                       "Only overall auPRC is printed; no stratum or uncertainty values.",
                       "The rule-based motif-scoring baseline used for this use case (for example MaxEntScan) is not evaluated."])
protocol("gel-prioritised-confirmation", "RNA-seq confirmation of SpliceAI2-prioritised rare variants in panel genes, Genomics England rare-disease participants (SpliceAI2 paper)",
         "Count how many rare variants prioritised by SpliceAI2 (> 0.25) in phenotype-matched panel genes show the predicted splicing change in the participant's RNA-seq.",
         {"protocol": "Participants with RNA-seq and monoallelic disorders, panels of up to 500 genes; rare variants with SpliceAI2 > 0.25 in panel genes are prioritised and checked in RNA-seq against 20 pooled controls lacking the variant (sashimi plots, Extended Data Fig. 5).",
          "version": "bioRxiv v1 Main text and Extended Data Fig. 5", "metric": "count", "metric_direction": "unknown", "unit": "count",
          "source_locator": "Main 'Contribution to rare genetic disease' paragraph 4; Fig. 4h,i; Extended Data Fig. 5"},
         "gel-rnaseq", areas=DNA_RNA, contexts=("clinical_research",),
         extra_limits=["SpliceAI2 only: no comparator model was put through the same prioritisation and confirmation.",
                       "The confirmation criterion for these 23 variants is described through sashimi plots against pooled controls; a numeric rule is not stated for this step.",
                       "Confirmation of a splicing change is not a diagnosis or a pathogenicity classification."])
protocol("population-constraint", "Depletion of high-scoring splice-proximal SNVs in gnomAD, TOPMed and UK Biobank, high-pLI genes (SpliceAI2 paper, Spearman)",
         "Spearman correlation between per-variant model score and combined multi-cohort allele count for splice-proximal SNVs in high-pLI genes; more negative means stronger depletion of high-scoring variants.",
         {"protocol": "Protein-coding SNVs within 30 bp of annotated splice sites, absent and common variants trinucleotide-matched; Spearman between score and raw multi-cohort allele count in genes with pLI > 0.8.",
          "version": "bioRxiv v1 Fig. 3c", "metric": "spearman-correlation", "metric_direction": "lower",
          "source_locator": "Methods 'Population genetics analysis'; Fig. 3c"},
         "population-constraint",
         extra_limits=["Proxy endpoint: purifying selection, not a measured splicing outcome.",
                       "SpliceAI and Pangolin use their standard scores here, not the position-resolved scores of the GT/AG and sQTL benchmarks."])
protocol("ukb-proteomics", "Carrier plasma protein levels for rare splice-region variants, UK Biobank (SpliceAI2 paper, Pearson)",
         "Pearson correlation between model score (loss positive, gain negative) at the nearest canonical splice site and mean carrier protein z-score for 6,149 rare splice-region variants; more negative means a closer match to reduced protein.",
         {"protocol": "VEP splice-region variants with allele frequency <= 0.1% carried by at least two individuals with Olink measurements; per-gene residualised protein levels; carriers of other rare coding variants in the gene excluded; Pearson between score and mean carrier z-score.",
          "version": "bioRxiv v1 Fig. 3f", "metric": "pearson-correlation", "metric_direction": "lower",
          "source_locator": "Methods 'UK Biobank proteomics analysis'; Fig. 3f"},
         "ukb-proteomics", extra_limits=["Proxy endpoint: plasma protein abundance, not a measured splicing outcome."])
protocol("gel-panel-enrichment", "Excess panel-matched rare variants in Genomics England rare-disease probands at panel-match odds ratio 2 (SpliceAI2 paper)",
         "Number of variants above a model threshold that fall in the proband's dominant disease-panel genes in excess of phenotype-shuffled expectation, at the threshold where the panel-match odds ratio is 2.",
         {"protocol": "Exclude essential splice, stop-gained, start-lost, frameshift and missense variants; compare prioritised variants in panel and non-panel genes between observed and ten phenotype-shuffled cohorts; OR = (A*D)/(B*C), excess = A - C*B/D; read at OR 2.",
          "version": "bioRxiv v1 Main text and Fig. 4b", "metric": "count", "metric_direction": "higher", "unit": "count",
          "source_locator": "Main 'Contribution to rare genetic disease' paragraphs 1 and 2; Methods 'Panel-matched disease gene enrichment'; Fig. 4b"},
         "gel-100kgp-dominant", contexts=("clinical_research",),
         extra_limits=["Proxy endpoint: enrichment in phenotype-matched genes, not confirmed splicing or diagnosis.",
                       "Only the SpliceAI2 value is printed; the text gives 114 for 'the next best model' without naming it, and the comparator curves in Fig. 4b are unlabelled."])
protocol("gtex-tissue-specific", "Tissue-specific junction usage differences across GTEx tissue pairs, held-out chromosomes (SpliceAI2 paper, Pearson)",
         "Pearson correlation between predicted and observed logit junction usage differences between tissue pairs.",
         {"protocol": "Junctions on chromosomes 1, 3, 5, 7 and 9 in genes up to 64 kb; 24 highest-usage tissues paired with 24 lowest; usage clipped to [1e-6, 1 - 1e-6], logit-transformed and differenced; junctions with fewer than 1,500 anchor reads in either tissue excluded.",
          "version": "bioRxiv v1 Main text and Fig. 2b", "metric": "pearson-correlation", "metric_direction": "higher",
          "source_locator": "Methods 'Prediction of tissue-specific junction usage'; Fig. 2b"},
         "gtex-tissue-junctions", areas=["rna-transcriptomes"],
         extra_limits=["SpliceAI2 only; no external comparator. Training-strategy variants are compared in Extended Data Fig. 4a (recorded as a claim).",
                       "Reference splicing, not variant effects."])
protocol("uvm-sf3b1", "SF3B1-associated junction usage differences in uveal melanoma, held-out genes (SpliceAI2 paper, Pearson)",
         "Pearson correlation between predicted and observed mutant-minus-wild-type junction usage differences, for junctions with a competing acceptor 10 to 30 nt away, a weak polypyrimidine tract and an A-rich branch point.",
         {"protocol": "Junctions with more than 500 anchor reads in held-out genes; differences clipped at 1e-4; cumulative filters for competing acceptor 10 to 30 nt, polypyrimidine fraction below 0.65 and branch point adenosine fraction at least 0.2.",
          "version": "bioRxiv v1 Main text and Fig. 2d", "metric": "pearson-correlation", "metric_direction": "higher",
          "source_locator": "Methods 'SF3B1-mutant uveal melanoma (UVM)'; Fig. 2d"},
         "tcga-uvm", areas=["rna-transcriptomes"], extra_limits=["SpliceAI2 only; correlations for the less filtered junction sets are figure-only."])
protocol("dm1-mbnl1", "MBNL1-associated junction usage differences across myotonic dystrophy severity groups, held-out genes (SpliceAI2 paper, Pearson)",
         "Pearson correlation between predicted and observed junction usage differences between healthy and three disease-severity groups.",
         {"protocol": "For each condition pair, junctions with more than 500 anchor reads and absolute measured logit difference above 0.01; usage clipped at 1e-4 before logit; Pearson per pair, mean over pairs reported in the text.",
          "version": "bioRxiv v1 Main text and Fig. 2e", "metric": "pearson-correlation", "metric_direction": "higher",
          "source_locator": "Methods 'MBNL1-depleted myotonic dystrophy'; Fig. 2e"},
         "dm1-gse86356", areas=["rna-transcriptomes"], extra_limits=["SpliceAI2 only; per-pair values are a heatmap without printed numbers."])

# ---------------------------------------------------------------- evaluations and results
EVALS = {}


def evaluation(proto, cfg, data_key, comparison, locator, name):
    id = P + "-eval-" + proto + "-" + cfg
    cmp = {"protocol_id": PR[proto], "adaptation": None, "budget": None}
    cmp.update(comparison)
    missing = {"comparison.budget": {"reason": "inapplicable", "note": "Pretrained scoring; no search or training budget"}}
    if cmp["adaptation"] is None:
        missing["comparison.adaptation"] = {"reason": "inapplicable", "note": "Pretrained weights; no adaptation to the benchmark"}
    for k, v in list(cmp.items()):
        if v is None and "comparison." + k not in missing:
            missing["comparison." + k] = {"reason": "unreported"}
    entity("evaluation", id, name, "Developer-reported comparison transcribed from the pinned source; not reproduced.",
           {"origin": "author_reported", "protocol": PR[proto], "version": "bioRxiv v1, retrieved 2026-10-13",
            "comparison": cmp, "source_locator": locator, "missing_metadata": missing},
           DNA_RNA if proto.startswith(("gtex-gtag", "gel", "opensplice")) else DNA,
           ["clinical_research"] if proto.startswith("gel") else ["research"],
           links=[{"relation": "system", "target_id": CONFIGS[cfg]}, {"relation": "assessment", "target_id": PR[proto]},
                  {"relation": "data", "target_id": D[data_key]}])
    EVALS[(proto, cfg)] = id
    return id


def result(eval_id, slug, name, printed, metric, direction, unit, qualifier, locator, method, method_note, numeric=None):
    id = eval_id.replace("-eval-", "-result-", 1) + "-" + slug
    a = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
         "numeric_value": numeric if numeric is not None else printed.replace("−", "-"),
         "source_locator": locator, "review": review(method, method_note),
         "missing_metadata": {"uncertainty": {"reason": "unreported"}}}
    if qualifier:
        a["metric_qualifier"] = qualifier
    add({"id": id, "kind": "result", "name": name, "description": "Developer-reported value transcribed from the pinned source. Not independently reproduced.",
         "status": "needs_review", "facets": {}, "source_ids": [SRC_ART], "links": [{"relation": "evaluation", "target_id": eval_id}],
         "attributes": a})
    claim_rows.append([id, SRC_ART, locator, printed, "result"])


ED2_NOTE = ("Deterministic parse of `pdftotext -layout` (poppler) text of page 52 of the pinned PDF: panel titles asserted in order, "
            "model row labels asserted, 17 values per row; column labels (rotated in the figure) read from a 130 dpi render of page 52. "
            "'All' column cross-checked against the Fig. 1d bar labels and the main-text statements (extract/build_batch.py).")
GT_INPUTS = {
    "spliceai-position-resolved": "SpliceAI 1.3.1 signed delta at the effect position, masking off",
    "pangolin-position-resolved": "Pangolin per-position prediction at the effect position, masking off",
    "alphagenome-composite-max": "AlphaGenome raw composite score, maximum aggregation, 1 Mb context",
    "alphagenome-splice-site-max": "AlphaGenome raw splice site score, maximum aggregation, 1 Mb context",
    "spliceai2-ensemble": "SpliceAI2 ensemble delta at the created site",
}
MODEL_CFG = {"SpliceAI": "spliceai-position-resolved", "Pangolin": "pangolin-position-resolved",
             "AlphaGenome": "alphagenome-composite-max", "SpliceAI2": "spliceai2-ensemble"}
OS_CFG = {"SpliceAI": "spliceai-opensplice-released", "Pangolin": "pangolin-opensplice-released",
          "AlphaGenome": "alphagenome-opensplice-released", "SpliceAI2": "spliceai2-ensemble"}
PANEL_DATA = {"gtex-gtag-detection": "gtex-gtag", "gtex-gtag-usage": "gtex-gtag", "gtex-sqtl-classification": "gtex-sqtl",
              "gtex-sqtl-effect-size": "gtex-sqtl", "opensplice-mpra": "opensplice-mpra"}
PANEL_CMP = {
    "gtex-gtag-detection": {"dataset_version": "GTEx WGS and RNA-seq (dbGaP phs000424.v9.p2), authors' GT/AG labels", "split": "None (pretrained scoring)",
                            "population": "4,545 cryptic and 573,967 null rare GT/AG-creating SNVs", "metric_implementation": "auPRC", "aggregation": "Pooled over variants"},
    "gtex-gtag-usage": {"dataset_version": "GTEx WGS and RNA-seq (dbGaP phs000424.v9.p2), authors' GT/AG labels", "split": "None (pretrained scoring)",
                        "population": "4,545 cryptic GT/AG-creating SNVs", "metric_implementation": "Spearman rank correlation with observed cryptic site usage", "aggregation": "Pooled over variants"},
    "gtex-sqtl-classification": {"dataset_version": "GTEx v8 sQTLs with SuSiE fine-mapping", "split": "None (pretrained scoring)",
                                 "population": "2,385 fine-mapped and 3,824 null SNVs within 50 bp of junction ends", "metric_implementation": "auROC", "aggregation": "Pooled over variants"},
    "gtex-sqtl-effect-size": {"dataset_version": "GTEx v8 sQTLs with SuSiE fine-mapping", "split": "None (pretrained scoring)",
                              "population": "2,385 fine-mapped SNVs", "metric_implementation": "Spearman rank correlation with tissue-averaged sQTL effect size", "aggregation": "Pooled over variants"},
    "opensplice-mpra": {"dataset_version": "OpenSplice MPRA (reference 23), release not printed", "split": "None (pretrained scoring)",
                        "population": "283,121 single-nucleotide substitutions in 599 exons", "metric_implementation": "Spearman rank correlation with measured delta PSI", "aggregation": "Pooled over variants"},
}
METRIC = {"gtex-gtag-detection": "auprc", "gtex-gtag-usage": "spearman-correlation", "gtex-sqtl-classification": "auroc",
          "gtex-sqtl-effect-size": "spearman-correlation", "opensplice-mpra": "spearman-correlation"}
QUAL = {"All": "all variants", "Exon": "exonic variants", "Near intronic": "near intronic variants (under 500 bp from the nearest exon)",
        "Deep intronic": "deep intronic variants (500 bp or more from the nearest exon)", "Intron": "intronic variants"}

col = 0
for proto, cols, title in ED2_PANELS:
    for m in MODELS:
        cfg = (OS_CFG if proto == "opensplice-mpra" else MODEL_CFG)[m]
        cmp = dict(PANEL_CMP[proto])
        cmp["inputs"] = ("Scores released with the OpenSplice dataset" if (proto == "opensplice-mpra" and m != "SpliceAI2")
                         else ("SpliceAI2 exon-skipping effect: mean of donor and acceptor usage changes at the flanking sites" if proto == "opensplice-mpra"
                               else GT_INPUTS[cfg] + "; essential splice variants excluded"))
        e = evaluation(proto, cfg, PANEL_DATA[proto], cmp, f"Extended Data Fig. 2, panel '{title}', row '{m}'; Fig. 1d",
                       f"{m} on {title.split(' (')[0]} ({METRIC[proto]}, SpliceAI2 paper)")
        for j, c in enumerate(cols):
            v = ED2[m][col + j]
            result(e, METRIC[proto] + "-" + re.sub(r"[^a-z]+", "-", c.lower()).strip("-"),
                   f"{m} {title} {c}", v, METRIC[proto], "higher", "unitless", QUAL[c] + "; essential splice variants excluded",
                   f"Extended Data Fig. 2 (page 52), panel '{title}', row '{m}', column '{c}'",
                   ["pdf-text-parse", "rendered-source-visual-check"], ED2_NOTE)
    col += len(cols)
assert col == 17

TEXT_NOTE = "Transcribed from the pinned text layer (pdftotext -layout); the sentence is asserted verbatim (whitespace-normalised) by extract/build_batch.py."
e = evaluation("gtex-gtag-detection", "alphagenome-splice-site-max", "gtex-gtag",
               dict(PANEL_CMP["gtex-gtag-detection"], inputs=GT_INPUTS["alphagenome-splice-site-max"] + "; essential splice variants excluded"),
               "Methods 'Evaluation of competing methods', AlphaGenome paragraph", "AlphaGenome raw splice site score on GTEx GT/AG (auPRC, SpliceAI2 paper)")
result(e, "auprc-all", "AlphaGenome raw splice site score GTEx GT/AG auPRC", "0.63", "auprc", "higher", "unitless",
       "all variants; essential splice variants excluded",
       "Methods 'Evaluation of competing methods', AlphaGenome paragraph: '... GTEx GT/AG auPRC (0.63) ...'", ["pdf-text-parse"], TEXT_NOTE)

FIG_NOTE = ("Printed bar label in the pinned PDF; label positions read with `pdftotext -bbox` and asserted to run left to right in "
            "legend order (SpliceAI, Pangolin, AlphaGenome, SpliceAI2), with bar colours checked on a 130 dpi render (extract/build_batch.py).")
GEL_CMP = {"dataset_version": "Genomics England NGRL rare-disease WGS and blood RNA-seq (project 754)", "split": "None (pretrained scoring)",
           "population": "3,065 cryptic and 1,775,800 null rare GT/AG-creating variants in 5,435 participants", "metric_implementation": "auPRC",
           "aggregation": "Pooled over variants"}
for m in MODELS:
    cfg = MODEL_CFG[m]
    e = evaluation("gel-gtag-detection", cfg, "gel-rnaseq", dict(GEL_CMP, inputs=GT_INPUTS[cfg] + "; essential splice variants excluded"),
                   f"Fig. 4g, bar '{m}'", f"{m} on Genomics England GT/AG cryptic splice activation (auPRC, SpliceAI2 paper)")
    result(e, "auprc", f"{m} GEL GT/AG auPRC", FIG4G[m], "auprc", "higher", "unitless", "all variants; essential splice variants excluded",
           f"Fig. 4g (page 17), bar label for '{m}'", ["pdf-text-parse", "rendered-source-visual-check"], FIG_NOTE)
e = evaluation("gel-gtag-detection", "alphagenome-splice-site-max", "gel-rnaseq",
               dict(GEL_CMP, inputs=GT_INPUTS["alphagenome-splice-site-max"] + "; essential splice variants excluded"),
               "Methods 'Evaluation of competing methods', AlphaGenome paragraph", "AlphaGenome raw splice site score on Genomics England GT/AG (auPRC, SpliceAI2 paper)")
result(e, "auprc", "AlphaGenome raw splice site score GEL GT/AG auPRC", "0.45", "auprc", "higher", "unitless",
       "all variants; essential splice variants excluded",
       "Methods 'Evaluation of competing methods', AlphaGenome paragraph: '... GEL GT/AG auPRC (0.45)'", ["pdf-text-parse"], TEXT_NOTE)

e = evaluation("gel-prioritised-confirmation", "spliceai2-ensemble", "gel-rnaseq",
               {"dataset_version": "Genomics England NGRL rare-disease WGS and RNA-seq (project 754)", "split": "None",
                "population": "Participants with RNA-seq, monoallelic disorders and up to 500 panel genes",
                "inputs": "SpliceAI2 summary score > 0.25 for rare variants in phenotype-matched panel genes",
                "metric_implementation": "Count of prioritised variants and of those with RNA-seq evidence of the predicted change", "aggregation": "Count"},
               "Main 'Contribution to rare genetic disease' paragraph 4; Extended Data Fig. 5", "SpliceAI2 prioritised variants confirmed in Genomics England RNA-seq")
result(e, "prioritised-count", "SpliceAI2 prioritised rare variants (GEL RNA-seq)", "23", "count", "unknown", "count",
       "rare variants prioritised at SpliceAI2 > 0.25 in panel genes", "Main 'Contribution to rare genetic disease' paragraph 4: '... yielded 23 prioritized rare variants ...'",
       ["pdf-text-parse"], TEXT_NOTE)
result(e, "confirmed-count", "SpliceAI2 prioritised variants with RNA-seq evidence (GEL)", "17", "true-positive-count", "higher", "count",
       "of the 23 prioritised variants, those showing RNA-seq evidence of the predicted splicing change",
       "Main 'Contribution to rare genetic disease' paragraph 4: '... of which 17 showed evidence of the predicted splicing change'", ["pdf-text-parse"], TEXT_NOTE)

POP_CFG = {"SpliceAI": "spliceai-standard", "Pangolin": "pangolin-standard", "AlphaGenome": "alphagenome-composite-max", "SpliceAI2": "spliceai2-ensemble"}
for m in MODELS:
    e = evaluation("population-constraint", POP_CFG[m], "population-constraint",
                   {"dataset_version": "gnomAD v3.1.2, TOPMed freeze 8 and UK Biobank combined", "split": "None",
                    "population": "Splice-proximal protein-coding SNVs in genes with pLI > 0.8, absent and common variants trinucleotide-matched",
                    "inputs": "Per-variant model score (" + {"SpliceAI": "standard SpliceAI delta score, masking off", "Pangolin": "Pangolin maximum absolute score, masking off",
                                                            "AlphaGenome": "AlphaGenome raw composite score", "SpliceAI2": "SpliceAI2 summary score"}[m] + ")",
                    "metric_implementation": "Spearman correlation between score and raw multi-cohort allele count", "aggregation": "Pooled over variants"},
                   f"Fig. 3c, bar '{m}'", f"{m} on splice-proximal SNV depletion in high-pLI genes (Spearman, SpliceAI2 paper)")
    result(e, "spearman", f"{m} multi-cohort allele count Spearman (high pLI)", FIG3C[m], "spearman-correlation", "lower", "unitless",
           "with multi-cohort raw allele count in high-pLI genes; more negative is better", f"Fig. 3c (page 15), bar label for '{m}'",
           ["pdf-text-parse", "rendered-source-visual-check"], FIG_NOTE)
for m in MODELS:
    e = evaluation("ukb-proteomics", MODEL_CFG[m], "ukb-proteomics",
                   {"dataset_version": "UK Biobank WGS and Olink plasma proteomics (application 33751)", "split": "None",
                    "population": "6,149 rare splice-region variants in 1,656 genes", "inputs": "Model delta at the nearest canonical splice site (GENCODE v39), loss positive and gain negative",
                    "metric_implementation": "Pearson correlation with mean carrier protein z-score", "aggregation": "Pooled over variants"},
                   f"Fig. 3f, bar '{m}'", f"{m} on UK Biobank carrier protein levels (Pearson, SpliceAI2 paper)")
    result(e, "pearson", f"{m} UK Biobank proteomics Pearson", FIG3F[m], "pearson-correlation", "lower", "unitless",
           "with mean carrier plasma protein z-score; more negative is better", f"Fig. 3f (page 15), bar label for '{m}'",
           ["pdf-text-parse", "rendered-source-visual-check"], FIG_NOTE)

e = evaluation("gel-panel-enrichment", "spliceai2-ensemble", "gel-100kgp-dominant",
               {"dataset_version": "Genomics England 100,000 Genomes Project (project 754), PanelApp 2023-04-25", "split": "None",
                "population": "7,504 probands with dominant panel genes; non-coding and synonymous rare variants after excluding essential splice, stop-gained, start-lost, frameshift and missense",
                "inputs": "SpliceAI2 summary score threshold giving panel-match odds ratio 2",
                "metric_implementation": "Excess = A - C*B/D against ten phenotype-shuffled cohorts", "aggregation": "Count"},
               "Main 'Contribution to rare genetic disease' paragraph 2; Fig. 4b", "SpliceAI2 excess panel-matched variants at odds ratio 2 (Genomics England)")
result(e, "excess-variants", "SpliceAI2 excess panel-matched variants at OR 2", "133", "count", "higher", "count",
       "excess panel-matched variants over phenotype-shuffled expectation at panel-match odds ratio 2",
       "Main 'Contribution to rare genetic disease' paragraph 2: 'At a fixed odds ratio of 2, SpliceAI2 recovered 133 excess variants'", ["pdf-text-parse"], TEXT_NOTE)

e = evaluation("gtex-tissue-specific", "spliceai2-tissue-147rbp", "gtex-tissue-junctions",
               {"dataset_version": "GTEx v8 junction counts, 48 tissues", "split": "Held-out chromosomes 1, 3, 5, 7 and 9",
                "population": "14,712,948 junction comparisons across tissue pairs", "inputs": "Sequence plus 147-RBP tissue signature",
                "adaptation": "Fine-tuned on chromosomes 2, 4, 6, 8, 10 to 22 and X", "metric_implementation": "Pearson on logit usage differences",
                "aggregation": "Pooled over junction-tissue-pair comparisons"},
               "Main 'Modeling tissue-specific splicing' paragraph 2; Fig. 2b", "SpliceAI2 tissue-specific fine-tune on GTEx tissue-pair junction usage differences")
for slug, printed, qual, loc in [
        ("pearson-all-pairs", "0.44", "all tissue pairs, 14,712,948 comparisons", "Main 'Modeling tissue-specific splicing' paragraph 2 '(Pearson r = 0.44; Fig. 2b)'; Fig. 2b panel 'All tissue pairs'"),
        ("pearson-cerebellum-blood", "0.58", "cerebellum versus blood, 13,770 junctions", "Main 'Modeling tissue-specific splicing' paragraph 2 '(13,770 splice junctions, Pearson r = 0.58)'; Fig. 2b panel 'Cerebellum vs blood'"),
        ("pearson-cortex-testis", "0.51", "cortex versus testis, 39,323 junctions", "Main 'Modeling tissue-specific splicing' paragraph 2 '(39,323 splice junctions, Pearson r = 0.51)'; Fig. 2b panel 'Cortex vs testis'")]:
    result(e, slug, "SpliceAI2 tissue-specific " + qual.split(",")[0], printed, "pearson-correlation", "higher", "unitless",
           "predicted versus observed logit junction usage difference, " + qual, loc, ["pdf-text-parse"], TEXT_NOTE)

e = evaluation("uvm-sf3b1", "spliceai2-sf3b1-uvm", "tcga-uvm",
               {"dataset_version": "TCGA-UVM via Genomic Data Commons", "split": "Held-out genes", "population": "Junctions with all three SF3B1-associated features (Fig. 2d, rightmost bar labelled 697)",
                "inputs": "Sequence plus SF3B1-mutant and wild-type 147-RBP signatures", "adaptation": "Fine-tuned on 18 mutant and 62 wild-type tumours",
                "metric_implementation": "Pearson on mutant-minus-wild-type usage differences", "aggregation": "Pooled over junctions"},
               "Main 'Modeling tissue-specific splicing' paragraph 4; Fig. 2d", "SpliceAI2 SF3B1 fine-tune on uveal melanoma junction usage differences")
result(e, "pearson-filtered", "SpliceAI2 SF3B1 uveal melanoma Pearson (filtered junctions)", "0.49", "pearson-correlation", "higher", "unitless",
       "junctions with competing acceptor 10 to 30 nt, weak polypyrimidine tract and A-rich branch point; held-out genes",
       "Main 'Modeling tissue-specific splicing' paragraph 4 '(Pearson r = 0.49; Fig. 2d)'", ["pdf-text-parse"], TEXT_NOTE)
e = evaluation("dm1-mbnl1", "spliceai2-dm1", "dm1-gse86356",
               {"dataset_version": "GEO GSE86356", "split": "Held-out genes", "population": "55 biopsies in four groups (healthy, low, medium and high severity)",
                "inputs": "Sequence plus four 147-RBP signatures", "adaptation": "Fine-tuned on 11 healthy and 44 affected individuals",
                "metric_implementation": "Pearson on logit usage differences per condition pair", "aggregation": "Mean over condition pairs"},
               "Main 'Modeling tissue-specific splicing' paragraph 4; Fig. 2e", "SpliceAI2 myotonic dystrophy fine-tune on MBNL1-associated junction usage differences")
result(e, "mean-pearson", "SpliceAI2 myotonic dystrophy mean Pearson across condition pairs", "0.26", "pearson-correlation", "higher", "unitless",
       "mean over disease-severity condition pairs; held-out genes",
       "Main 'Modeling tissue-specific splicing' paragraph 4 '(mean Pearson r = 0.26)'", ["pdf-text-parse"], TEXT_NOTE)

# ---------------------------------------------------------------- descriptive claims
claim(P + "-claim-training-data", "SpliceAI2 training data", MODEL, "training_data",
      "Trained on splice site and junction usage from 314,745 short-read RNA-seq samples (67,493,026 junctions) in human and nine other mammalian species, and on transcript usage from 330 ENCODE long-read samples in human and mouse. Human: 127,431 samples from recount3 (GTEx, TCGA, CCLE and other SRA-derived projects).",
      "Main 'Hierarchical model of RNA splicing' paragraph 1; Methods 'Training datasets'; Supplementary Table 1 rows 'Homo_sapiens' and 'Total'",
      sources=(SRC_ART, SRC_TSV), note="Text asserted in the pinned PDF; Supplementary Table 1 totals and the human row asserted in the pinned TSV (extract/build_batch.py).")
claim(P + "-claim-training-split", "SpliceAI2 training split and benchmark overlap", MODEL, "training_split",
      "Genes on human chromosomes 21 and 22 were held out for validation and all other genes were used for training. The variant benchmarks (GTEx and GEL GT/AG, GTEx sQTL, OpenSplice, UK Biobank) are not restricted to held-out chromosomes, so most benchmark variants lie in genes seen in training; only the top-transcript benchmark is restricted to chromosomes 21 and 22. The paper does not say whether junctions observed in GTEx benchmark samples were excluded from training.",
      "Methods 'SpliceAI2 model' (Training, last paragraph), 'Top transcript benchmark' and 'Variant effect benchmarks'; Supplementary Table 1 row 'Homo_sapiens'",
      sources=(SRC_ART, SRC_TSV), note="Split sentence asserted verbatim; the overlap statement is the extractor's reading of the Methods and needs reviewer confirmation.")
claim(P + "-claim-licence", "SpliceAI2 licence and intended use", MODEL, "licence",
      "SpliceAI2 code, weights and precomputed scores are licensed under the SpliceAI2 Model Terms of Use: only for non-commercial use by or for non-commercial organisations, excluding for-profit companies, contract research organisations and commercial healthcare providers or laboratories; no redistribution or hosting; labelled research use only and not for use in diagnostic procedures.",
      "LICENSE preamble and sections 2, 3 and 13; README paragraph 2", sources=(SRC_LICENCE, SRC_README),
      sha256="70298b77bd30d2ddfbe01d67b100363599b0b98ccb920e859abcf2a9d15a9c36",
      url="https://raw.githubusercontent.com/Illumina/SpliceAI2/1dcd2a1882a8223095e7529982ae70bcb658340a/LICENSE",
      method=("transcription",), note="Summarised from the pinned LICENSE and README text by the extractor.")
claim(P + "-claim-alphagenome-oxford", "AlphaGenome scoring in the SpliceAI2 paper", CONFIGS["alphagenome-composite-max"], "evaluation_actor",
      "All AlphaGenome analyses were conducted at the University of Oxford by co-authors Y.K. and E.M.W., supervised by S.J.S.; the raw composite score with maximum aggregation was chosen from 40 scoring configurations as best on average across eight evaluations.",
      "Methods 'Evaluation of competing methods', AlphaGenome paragraph; Author contributions")
claim(P + "-claim-top-transcript", "SpliceAI2 top-transcript reconstruction", MODEL, "top_transcript_reconstruction",
      "Perfectly reconstructed the most abundant transcript for 82% of held-out genes (chromosomes 21 and 22, n = 352), compared with 78% when trained without long-read data (human-only models).",
      "Main 'Hierarchical model of RNA splicing' paragraph 2; Methods 'Top transcript benchmark'; Fig. 1c")
claim(P + "-claim-rare-disease-burden", "SpliceAI2 share of excess rare-disease burden", PR["gel-panel-enrichment"], "excess_burden_share",
      "Among excess panel-matched variants, protein-truncating variants accounted for 50% and SpliceAI2-identified cryptic splice variants a further 15%; half of those cryptic splice variants lie more than 50 bp into introns. At panel-match odds ratio 2 the next best model recovered 114 excess variants; the text does not name it.",
      "Main 'Contribution to rare genetic disease' paragraphs 2 and 3; Fig. 4e")
claim(P + "-claim-tissue-ablations", "SpliceAI2 tissue-specific training-strategy and variant-effect checks", PR["gtex-tissue-specific"], "ablation_results",
      "Extended Data Fig. 4a prints Pearson r 0.37 (one-hot, from scratch), 0.38 (147 RBP, from scratch), 0.43 (one-hot, fine-tune) and 0.44 (147 RBP, fine-tune). Extended Data Fig. 4c prints Pearson r 0.5393 for ridge regression on measured reference usage alone and 0.5395 with SpliceAI2 tissue predictions added; the authors state there was no additional benefit from tissue-specific predictions for tissue-specific variant effects.",
      "Extended Data Fig. 4a and 4c (page 55); Main 'Modeling tissue-specific splicing' paragraph 5",
      method=("pdf-text-parse", "rendered-source-visual-check"), note="Bar labels present in the pinned text layer of page 55 (asserted); bar order read from the render.")
claim(P + "-claim-dm1-severity", "SpliceAI2 myotonic dystrophy severity contrast", PR["dm1-mbnl1"], "severity_contrast",
      "Correlations increased between groups with greater differences in disease severity (Pearson r = 0.42; Fig. 2e). The text does not name the condition pair, and the Fig. 2e heatmap prints no values.",
      "Main 'Modeling tissue-specific splicing' paragraph 4; Fig. 2e")

# ---------------------------------------------------------------- relevance judgements (drafts)
JUDGE = P.replace("rna-splicing-", "use-case-mapping-rna-splicing-")


def judgement(key, use_case, proto_key, relevance, endpoint, rationale, constraints, limitations, locators, group, title, stratum, order, headline):
    id = JUDGE + "-" + key
    add({"id": id, "kind": "claim",
         "name": f"Relevance of {records[[r['id'] for r in records].index(PR[proto_key])]['name']} to use case {use_case}",
         "description": rationale, "status": "needs_review", "facets": {}, "source_ids": [SRC_ART],
         "links": [{"relation": "subject", "target_id": use_case}],
         "attributes": {"field": "links:assessed_by:" + PR[proto_key], "value": PR[proto_key], "relevance": relevance,
                        "endpoint": endpoint, "rationale": rationale, "constraints": constraints, "limitations": limitations,
                        "citation_locators": [{"source_id": SRC_ART, "locator": l} for l in locators],
                        "source_locator": "; ".join(SRC_ART + ": " + l for l in locators),
                        "comparison_group": group, "comparison_title": title, "stratum_label": stratum, "stratum_order": order,
                        "headline_metric": headline,
                        "reason": "Drafted from the 2026-10-13 SpliceAI2 extraction (data/omics/use-case-coverage-rna-splicing-20261013-spliceai2), issue #127. Pending independent review.",
                        "review": review(["scope-review"], "Drafted by the extractor against the use case's question, inputs and output and the existing judgements for the same use case; not a review.")}})
    claim_rows.append([id, SRC_ART, "; ".join(locators), relevance, "judgement"])


BASE_CONSTRAINTS = ["Inspect every linked evaluation's source locator and configuration before citing a result.",
                    "Do not combine this mapping's evaluations with any other protocol's results; truth sets, inputs and metrics differ between sources."]
judgement("gel-gtag", "use-case-patient-rna-splicing-validation", "gel-gtag-detection", "proxy",
          "auPRC for separating RNA-seq-confirmed cryptic splice gains from null rare GT/AG-creating variants in 5,435 Genomics England rare-disease participants with WGS and blood RNA-seq, for SpliceAI, Pangolin, AlphaGenome and SpliceAI2 on the same variants",
          "Closest evidence in the paper to this use case: DNA-based predictors scored against splicing observed in rare-disease participants' own RNA-seq, all four tools on the same variants. Proxy, as for Drost et al. 2025: the systems take DNA variants rather than patient RNA, the endpoint is cryptic-site activation by GT/AG-creating variants only, and the authors developed SpliceAI2 and built the benchmark.",
          BASE_CONSTRAINTS + ["Compare configurations only within this protocol; the AlphaGenome raw splice site score (0.45) is a separate configuration reported in the Methods, not the paper's chosen AlphaGenome score (0.36)."],
          ["Developer-reported; the SpliceAI2 authors built the labels and ran SpliceAI, Pangolin and SpliceAI2; AlphaGenome was run by Oxford co-authors.",
           "Training overlap: SpliceAI2 was trained on all human genes outside chromosomes 21 and 22; benchmark variants are genome-wide.",
           "Blood RNA-seq only, so splicing in genes not expressed in blood is unobserved; GT/AG-creating variants only; essential splice variants excluded.",
           "The use case's baseline (FRASER and OUTRIDER on patient RNA, with a legacy splice-site vote such as MaxEntScan on DNA) is not evaluated in this paper; no rule-based motif scorer is compared (see issue #121).",
           "Controlled-access data (Genomics England project 754); benchmark variant lists are not released, so the comparison cannot be rerun outside the Research Environment.",
           "Single auPRC per model; no uncertainty, strata or thresholds printed.",
           "Preprint (bioRxiv v1), not peer reviewed."],
          ["Fig. 4g", "Main 'Contribution to rare genetic disease' paragraph 4", "Methods 'Evaluation of competing methods' and 'Variant effect benchmarks'"],
          "spliceai2-2026-gel", "DNA splice predictors against cryptic splicing in Genomics England rare-disease blood RNA-seq (SpliceAI2 paper, developer-reported)",
          "GT/AG cryptic-site activation, all four models", 1, "auprc")
judgement("gel-prioritised", "use-case-patient-rna-splicing-validation", "gel-prioritised-confirmation", "proxy",
          "Number of rare variants prioritised by SpliceAI2 (> 0.25) in phenotype-matched panel genes and the number with RNA-seq evidence of the predicted splicing change (23 and 17)",
          "Shows how often SpliceAI2-prioritised candidates in rare-disease participants were supported by the participant's own RNA-seq, the follow-up step this use case is about. Proxy: one tool only, a single threshold, and confirmation of a splicing change rather than a diagnosis.",
          BASE_CONSTRAINTS + ["Do not read 17 of 23 as a precision for other tools; no comparator was put through the same prioritisation."],
          ["SpliceAI2 only; SpliceAI and Pangolin were not evaluated on this prioritisation.",
           "23 variants; no confidence interval.",
           "Confirmation is shown with sashimi plots against 20 pooled controls; a numeric confirmation rule for these variants is not stated.",
           "Developer-reported; controlled-access Genomics England data (project 754).",
           "Training overlap: SpliceAI2 was trained on all human genes outside chromosomes 21 and 22.",
           "Preprint (bioRxiv v1), not peer reviewed."],
          ["Main 'Contribution to rare genetic disease' paragraph 4", "Fig. 4h,i", "Extended Data Fig. 5"],
          "spliceai2-2026-gel", "DNA splice predictors against cryptic splicing in Genomics England rare-disease blood RNA-seq (SpliceAI2 paper, developer-reported)",
          "SpliceAI2-prioritised variants checked in RNA-seq", 2, "true-positive-count")
judgement("opensplice", "use-case-splicing-follow-up", "opensplice-mpra", "proxy",
          "Spearman correlation between predicted and measured exon-inclusion change (delta PSI) for 283,121 single-nucleotide substitutions across 599 exons in the OpenSplice MPRA, for SpliceAI, Pangolin, AlphaGenome and SpliceAI2",
          "Experimentally measured splicing of human SNVs in a reporter assay, with four predictors on the same variants: the same kind of endpoint as the MFASS reporter evidence for choosing variants for a splicing experiment. Proxy: a rank correlation over all substitutions, not precision among variants selected for follow-up, and the comparator scores are those released with OpenSplice while SpliceAI2 was scored by its developers.",
          BASE_CONSTRAINTS + ["Do not pool with the MFASS protocols; assay, exons and metric differ.",
                              "Settings differ between systems: comparators use the OpenSplice-released scores, SpliceAI2 an exon-skipping formula from its own outputs."],
          ["Developer-reported; the OpenSplice dataset is from another group (reference 23), but this comparison was run by the SpliceAI2 authors.",
           "Spearman over all substitutions; no precision at a follow-up capacity and no uncertainty printed.",
           "Training overlap: SpliceAI2 was trained on all human genes outside chromosomes 21 and 22, including the reference splicing of most OpenSplice exons' genes.",
           "The use case's baseline, MaxEntScan, is not evaluated.",
           "Preprint (bioRxiv v1), not peer reviewed."],
          ["Extended Data Fig. 2 panel 'OpenSplice MPRA (ρ)'", "Fig. 1d", "Methods 'Variant effect benchmarks', OpenSplice MPRA paragraph"],
          "spliceai2-2026-opensplice", "OpenSplice MPRA delta PSI (SpliceAI2 paper, developer-reported)",
          "All substitutions and exon or intron strata", 1, "spearman-correlation")

# ---------------------------------------------------------------- write
records.sort(key=lambda r: r["id"])
for r in records:  # the store keeps missing_metadata keys sorted
    if "missing_metadata" in r["attributes"]:
        r["attributes"]["missing_metadata"] = dict(sorted(r["attributes"]["missing_metadata"].items()))
with open(os.path.join(out, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claim_rows.sort()
with open(os.path.join(out, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claim_rows)
counts = {}
for r in records:
    counts[r["kind"]] = counts.get(r["kind"], 0) + 1
print(json.dumps(dict(sorted(counts.items())), indent=1), len(records))
