"""Extract the BERTax (Mock et al., PNAS 2022) method comparison into batch records.

Inputs (pinned, passed as arguments):
  1. table1.txt: the text layer of Table 1 from the PNAS version-of-record PDF
     (sha256 7977424613ab5e5f4986745b527a270fd2c0427dbab40471813903eda85dcaec), read with pdf.js 4.0.379
  2. si.txt: `pdftotext -layout` (poppler) of the SI appendix PDF
     (sha256 89a2f86f66cbb2ff17886d413cd89577285086fedd1009e1d9daf87b29fbc1c0)
  3. output directory (the batch folder)

Every row label, column header and field count is asserted before a value is written.
Run with python3 -I. Writes batch.jsonl and claims.csv.
"""
import csv
import json
import re
import sys

table1_path, si_path, out_dir = sys.argv[1:4]
DATE = "2026-10-12"
P = "dna-pathogen-20261012-bertax"
SRC = f"{P}-source"
SRC_PDF = f"{P}-source-pdf"
SRC_SI = f"{P}-source-si"
XML_SHA = "c0bb2f1bba8680b300076292389b39346ae58bea4bdf28647dd9462333b3bcd7"
PDF_SHA = "7977424613ab5e5f4986745b527a270fd2c0427dbab40471813903eda85dcaec"
SI_SHA = "89a2f86f66cbb2ff17886d413cd89577285086fedd1009e1d9daf87b29fbc1c0"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9436379/fullTextXML"
PDF_URL = "https://www.pnas.org/doi/pdf/10.1073/pnas.2122636119"
SI_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9436379/supplementaryFiles"
FACETS = {"areas": ["microbes-communities"], "contexts": ["research"]}
REVIEWER_NOTE = ("Extracting Claude agent for the 2026-10-12 ML-versus-baseline pass (issue #121); "
                 "extraction only, not a review. Pending an independent review-evidence pass.")

records, claims_rows = [], []


def add(record):
    records.append(record)
    return record


def review(method, note, sha, url):
    return {"method": method, "method_note": note, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
            "date": DATE, "artifact_sha256": sha, "retrieval_url": url,
            "note": "Extracted, not reviewed. The review-evidence pass must re-check this value against the pinned artifact."}


# ---------------------------------------------------------------- parse Table 1 (PDF text layer)
t1 = [line.rstrip() for line in open(table1_path, encoding="utf-8")]
assert t1[0].strip() == "Table 1.   Comparison of the macro AveP on all three datasets", t1[0]
assert t1[2].split() == ["Closely", "related", "Distantly", "related", "Final"], t1[2]
assert t1[3].split() == ["Tool", "Supk.", "Phyl.", "Supk.", "Phyl.", "Supk.", "Phyl.", "Genus"], t1[3]
T1_COLS = [("closely", "superkingdom"), ("closely", "phylum"), ("distantly", "superkingdom"),
           ("distantly", "phylum"), ("final", "superkingdom"), ("final", "phylum"), ("final", "genus")]
T1_ROWS = [("MMseqs2", "mmseqs2"), ("MMseqs2 tax. ∗", "mmseqs2-taxonomy"), ("minimap2", "minimap2"),
           ("Kraken2", "kraken2"), ("sourmash", "sourmash"), ("DeepMicrobes", "deepmicrobes"),
           ("BERTax", "bertax")]
table1 = {}
line_no = 4
for label, tool in T1_ROWS:
    line = t1[line_no]
    assert line.startswith(label + "   "), (label, line)
    values = line[len(label):].split()
    assert len(values) == 7 and all(re.fullmatch(r"\d+\.\d\d", v) for v in values), line
    table1[tool] = (label, values)
    line_no += 1
assert t1[line_no].strip() == "MMseqs2+", t1[line_no]
for label, tool in [("DeepMicrobes", "mmseqs2-deepmicrobes"), ("BERTax", "mmseqs2-bertax")]:
    line = t1[line_no + 1]
    assert line.startswith(label + "   "), (label, line)
    values = line[len(label):].split()
    assert len(values) == 7 and all(re.fullmatch(r"\d+\.\d\d", v) for v in values), line
    table1[tool] = ("MMseqs2+ " + label, values)
    line_no += 1
assert t1[line_no + 1].split()[0] == "random"  # chance reference row, not a method; not extracted

# ---------------------------------------------------------------- parse SI Tables S2 and S5
si = open(si_path, encoding="utf-8").read().splitlines()


def block(title_start, labels, n_values):
    start = next(i for i, l in enumerate(si) if l.startswith(title_start))
    rows = {}
    for label in labels:
        i = next(j for j in range(start, start + 40) if re.match(r"\s*" + re.escape(label) + r"\s{2,}\d", si[j]))
        values = si[i].strip()[len(label):].split()
        assert len(values) == n_values and all(re.fullmatch(r"\d+(\.\d\d)?", v) for v in values), si[i]
        rows[label] = values
    return start, rows


S2_LABELS = [("MMseqs2", "mmseqs2"), ("MMseqs2 taxonomy∗", "mmseqs2-taxonomy"), ("minimap2", "minimap2"),
             ("Kraken2", "kraken2"), ("sourmash", "sourmash"), ("DeepMicrobes", "deepmicrobes"),
             ("BERTax", "bertax"), ("MMseqs2 + DeepMicrobes", "mmseqs2-deepmicrobes"),
             ("MMseqs2 + BERTax", "mmseqs2-bertax")]
s2_start, s2 = block("Table S2: Comparison of the accuracy (acc.) and the proportion (prop.)",
                     [l for l, _ in S2_LABELS], 8)
assert si[s2_start + 3].split() == ["closely", "related", "dataset", "distantly", "related", "dataset"]
assert si[s2_start + 4].split() == ["Tool", "superkingdom", "phylum", "superkingdom", "phylum"]
assert si[s2_start + 5].split() == ["acc.", "prop."] * 4
S2_COLS = [(d, rank, m) for d in ("closely", "distantly") for rank in ("superkingdom", "phylum")
           for m in ("acc.", "prop.")]
S5_LABELS = [("BERTax", "bertax"), ("DeepMicrobes", "deepmicrobes"), ("MMseqs2 taxonomy∗", "mmseqs2-taxonomy")]
s5_start, s5 = block("Table S5: Comparison of accuracy (acc.) when removing potentially homologous",
                     [l for l, _ in S5_LABELS], 6)
header = next(si[j] for j in range(s5_start, s5_start + 15) if si[j].strip().startswith("Tool"))
assert header.split() == ["Tool"] + ["acc.", "unfiltered", "acc.", "filtered", "acc.", "left-out"] * 2, header
S5_COLS = [(rank, sub) for rank in ("superkingdom", "phylum") for sub in ("unfiltered", "filtered", "left-out")]

# ---------------------------------------------------------------- sources
add({"id": SRC, "kind": "source",
     "name": "Taxonomic classification of DNA sequences beyond sequence similarity using deep neural networks",
     "description": "Primary source (Europe PMC full-text XML) retrieved and hashed for the 2026-10-12 ML-versus-baseline pass.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {"url": "https://doi.org/10.1073/pnas.2122636119", "artifact_url": XML_URL,
                    "version": "PNAS 119(35):e2122636119, published 2022-08-26; PMC9436379 full-text XML",
                    "retrieved_at": "2026-10-12T20:51:54Z", "artifact_sha256": XML_SHA,
                    "doi": "10.1073/pnas.2122636119", "publication_status": "peer_reviewed",
                    "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml", "venue": "PNAS", "year": 2022,
                    "source_locator": "Licence statement in the article XML <license> element: CC BY-NC-ND 4.0",
                    "limitations": ["Table 1 is an image in the XML (table1.jpg); its values are taken from the PNAS PDF, recorded separately."],
                    "access_note": "Open access under CC BY-NC-ND 4.0. Full text is not archived in the batch; only factual table excerpts are."}})
add({"id": SRC_PDF, "kind": "source",
     "name": "Taxonomic classification of DNA sequences beyond sequence similarity using deep neural networks (PNAS PDF)",
     "description": "Version-of-record PDF, used for Table 1, whose PMC copy is an image.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {"url": "https://doi.org/10.1073/pnas.2122636119", "artifact_url": PDF_URL,
                    "version": "PNAS 119(35):e2122636119 version-of-record PDF (10 pages)",
                    "retrieved_at": "2026-10-12T20:56:37Z", "artifact_sha256": PDF_SHA,
                    "doi": "10.1073/pnas.2122636119", "publication_status": "peer_reviewed",
                    "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf", "venue": "PNAS", "year": 2022,
                    "retrieval_method": "Fetched in a Chrome session (Claude in Chrome) from the article page, because PNAS returns HTTP 403 to command-line clients; SHA-256 computed in the page with crypto.subtle; text layer read with pdf.js 4.0.379.",
                    "retrieval_note": "The bytes were not saved to disk. A reviewer must re-fetch the PDF through a browser and compare its SHA-256.",
                    "source_locator": "Page 4, Table 1 'Comparison of the macro AveP on all three datasets'"}})
add({"id": SRC_SI, "kind": "source",
     "name": "BERTax SI Appendix (pnas.2122636119.sapp.pdf)",
     "description": "Supplementary Information PDF of the BERTax article.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {"url": "https://doi.org/10.1073/pnas.2122636119", "artifact_url": SI_URL,
                    "version": "SI Appendix as distributed with PMC9436379 (member pnas.2122636119.sapp.pdf of the Europe PMC supplementaryFiles ZIP)",
                    "retrieved_at": "2026-10-12T20:55:54Z", "artifact_sha256": SI_SHA,
                    "doi": "10.1073/pnas.2122636119", "publication_status": "peer_reviewed",
                    "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf", "venue": "PNAS", "year": 2022,
                    "hash_scope": "SHA-256 of the PDF member, not of the ZIP (the ZIP is rebuilt per request)",
                    "source_locator": "Pages S15-S16, Tables S2 and S5"}})

# ---------------------------------------------------------------- systems
add({"id": f"{P}-model-bertax", "kind": "model", "name": "BERTax",
     "description": "BERT encoder pretrained on 1,500-nt genome fragments (3-mer tokens) and fine-tuned to predict superkingdom, phylum and, in the final model, genus.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["supervised_machine_learning"]},
     "source_ids": [SRC], "links": [],
     "attributes": {"reported_name": "BERTax", "entity_level": "family",
                    "source_locator": "Results 'Best Architecture Based on Simultaneous Classifications of Taxonomic Ranks'; Materials and Methods 'Pretraining', 'Architectures', 'Downloadable BERTax Version'",
                    "access": "Code at https://github.com/f-kretschmer/bertax (GPL-3.0 per the repository; not pinned in this pass)",
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; each configuration is one trained model"}}}})
add({"id": f"{P}-model-deepmicrobes", "kind": "model", "name": "DeepMicrobes",
     "description": "Taxonomic classifier using 12-mer embeddings, bidirectional LSTM layers and self-attention (Liang et al.), retrained by the BERTax authors on the BERTax training data.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["supervised_machine_learning"]},
     "source_ids": [SRC], "links": [],
     "attributes": {"reported_name": "DeepMicrobes", "entity_level": "family",
                    "source_locator": "Materials and Methods 'Comparison to Other Tools' paragraph 1",
                    "missing_metadata": {"version": {"reason": "unreported", "note": "No DeepMicrobes version or commit is given"}}}})
for pid, name, desc in [
        ("mmseqs2-bertax", "MMseqs2 + BERTax", "MMseqs2 classifies each sample first; samples MMseqs2 cannot classify are passed to BERTax."),
        ("mmseqs2-deepmicrobes", "MMseqs2 + DeepMicrobes", "MMseqs2 classifies each sample first; samples MMseqs2 cannot classify are passed to DeepMicrobes.")]:
    add({"id": f"{P}-pipeline-{pid}", "kind": "pipeline", "name": name, "description": desc,
         "status": "needs_review",
         "facets": {**FACETS, "method_types": ["conventional_pipeline", "supervised_machine_learning"]},
         "source_ids": [SRC], "links": [],
         "attributes": {"reported_name": name, "configuration_type": "pipeline",
                        "source_locator": "Results 'Comparison to Other Classification Approaches' paragraph 3",
                        "missing_metadata": {"version": {"reason": "unreported", "note": "Combination defined in the article; no software release"}}}})

TOOLS = {
    "mmseqs2": ("MMseqs2", "discovery-model-mmseqs2", ["conventional_pipeline"], "MMseqs2 with default parameters (k-mers and local alignment) against the dataset's training partition as reference"),
    "mmseqs2-taxonomy": ("MMseqs2 taxonomy*", "discovery-model-mmseqs2", ["conventional_pipeline"], "MMseqs2 with the parameters of MMseqs2 taxonomy (--e-profile 0.001, -e 1), so each hit carries an E value used for the PR curve; same hits as MMseqs2 taxonomy for 99.94% of samples"),
    "minimap2": ("minimap2", "dna-pathogen-20261009-method-minimap2", ["conventional_pipeline"], "minimap2 with default parameters; the most similar reference sequence gives the taxonomy"),
    "kraken2": ("Kraken2", "catalog-model-kraken2", ["conventional_pipeline"], "Kraken2 with default parameters; database built from the dataset's training partition"),
    "sourmash": ("sourmash", "dna-pathogen-20261009-method-sourmash", ["conventional_pipeline"], "sourmash with default parameters; reference built from the dataset's training partition"),
    "deepmicrobes": ("DeepMicrobes", f"{P}-model-deepmicrobes", ["supervised_machine_learning"], "Architecture and hyperparameters evaluated as best by Liang et al.; trained on exactly the same data as BERTax"),
    "bertax": ("BERTax", f"{P}-model-bertax", ["supervised_machine_learning"], "All-in-one architecture: 12 transformer blocks, 5 attention heads, embedding dimension 250, fine-tuned for at most 16 epochs with early stopping and class weights"),
    "mmseqs2-deepmicrobes": ("MMseqs2 + DeepMicrobes", f"{P}-pipeline-mmseqs2-deepmicrobes", ["conventional_pipeline", "supervised_machine_learning"], "MMseqs2 first; unclassified samples passed to DeepMicrobes trained on the same dataset"),
    "mmseqs2-bertax": ("MMseqs2 + BERTax", f"{P}-pipeline-mmseqs2-bertax", ["conventional_pipeline", "supervised_machine_learning"], "MMseqs2 first; unclassified samples passed to BERTax trained on the same dataset"),
}
DATASETS = {
    "closely": ("closely related", "Closely related dataset",
                "Test set of 2,000 randomly selected samples per phylum; 95% of the remaining samples train and 5% validate; test and training samples may share a genus.",
                "30 phylum classes with at least 10,000 fragments (2,328,584 samples before partitioning)"),
    "distantly": ("distantly related", "Distantly related dataset",
                  "Per phylum, one or more whole genera (the subset closest to 2,000 samples) form the test set, undersampled to 1,780 samples per phylum; no test sample shares a genus with the training set.",
                  "Same 30 phylum classes as the closely related dataset"),
    "final": ("final", "Final model dataset",
              "Closely related selection on an expanded fragment set (additional 2 million eukaryotic and bacterial fragments); classes with fewer than 10,000 fragments are pooled into an 'unknown' class at each rank.",
              "5 superkingdom, 44 phylum and 156 genus classes, including 'unknown'"),
}
CONFIG_LOCATOR = "Materials and Methods 'Comparison to Other Tools' paragraphs 1-2; Results 'Comparison to Other Classification Approaches' paragraphs 1 and 3"

for d, (dlabel, dname, split, population) in DATASETS.items():
    add({"id": f"{P}-data-{d}", "kind": "dataset", "name": f"BERTax {dname} (Mock et al. 2022)",
         "description": "1,500-nt genome fragments from NCBI RefSeq genomes of archaea, bacteria, eukaryotes and viruses, clustered at 80% identity with MMseqs2-linclust.",
         "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
         "attributes": {"version": "As described in Mock et al. 2022 (genome list and assembly versions in Dataset S1)",
                        "population": population, "split": split,
                        "access": "Genome list in Dataset S1 (pnas.2122636119.sd01.xlsx); the fragment sets themselves are not linked in the article",
                        "source_locator": "Materials and Methods 'Data', 'Pretraining Dataset', 'Preparing Data for Fine-Tuning', 'Three Evaluation Datasets'; Table 2; Fig. 4"}})

add({"id": f"{P}-benchmark", "kind": "benchmark",
     "name": "BERTax taxonomic classification of genome fragments (Mock et al. 2022)",
     "description": "Superkingdom, phylum and genus assignment of 1,500-nt genome fragments, with every tool given the same reference or training data.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
     "attributes": {"entity_level": "suite", "version": "PNAS 2022, Table 1 and SI Tables S2 and S5",
                    "task": "Assign a DNA fragment to its superkingdom, phylum or genus",
                    "source_locator": "Results 'Comparison to Other Classification Approaches'; Materials and Methods 'Three Evaluation Datasets', 'Comparison to Other Tools'",
                    "scope_note": "Architecture comparisons (SI Table S1), per-superkingdom AveP (S3), homology splits for BERTax only (S6) and ablations (S7) compare BERTax variants only and were not extracted. Figures and PR curves were not read.",
                    "limitations": ["Inputs are simulated 1,500-nt genome fragments, not sequencing reads or clinical specimens.",
                                    "Database tools were given only the training partition as reference, not whole genomes; the authors call this a necessary deviation from their designed use.",
                                    "Classification is at superkingdom, phylum and genus level, not species or strain."]}})

PROTO = {}
for d, (dlabel, dname, split, population) in DATASETS.items():
    ranks = "superkingdom and phylum" + (", and genus" if d == "final" else "")
    metrics = "macro AveP (Table 1)" + ("" if d == "final" else ", accuracy and proportion of samples classified (SI Table S2)") + \
              (", and accuracy after removing test sequences with a BLAST hit to the training partition (SI Table S5)" if d == "distantly" else "")
    pid = f"{P}-protocol-{d}"
    PROTO[d] = pid
    add({"id": pid, "kind": "protocol", "name": f"BERTax {dname}: taxonomic classification at {ranks} (Mock et al. 2022)",
         "description": f"Each tool classifies the {dlabel} test fragments using only that dataset's training partition; scored by {metrics}.",
         "status": "needs_review", "facets": FACETS, "source_ids": [SRC, SRC_PDF, SRC_SI],
         "links": [{"relation": "uses_data", "target_id": f"{P}-data-{d}"}, {"relation": "part_of", "target_id": f"{P}-benchmark"}],
         "attributes": {"protocol": "Only each tool's top prediction per sample is used. For the PR curves and AveP, samples a tool does not classify are treated as random guesses. Macro AveP is the mean of per-class average precision, one-versus-all.",
                        "version": "Table 1" + ("" if d == "final" else "; SI Table S2") + ("; SI Table S5" if d == "distantly" else ""),
                        "metric_definition": "Macro AveP: unweighted mean over classes of per-class average precision of the PR curve. acc.: accuracy; prop.: proportion of samples a tool returned a prediction for.",
                        "source_locator": "SI Appendix 'Details to PR-curve plots' (General Remarks; macro-average PR curves); Table 1 footnote; SI Table S2 caption",
                        "limitations": ["The SI caption does not say whether 'acc.' is computed over all samples or only the samples a tool classified; the main text describes a trade-off between accuracy and the proportion classified."]}})

CONFIG = {}
for d, (dlabel, dname, _, _) in DATASETS.items():
    tools = list(TOOLS)
    for tool in tools:
        name, target, mtypes, params = TOOLS[tool]
        cid = f"{P}-config-{tool}-{d}"
        CONFIG[(tool, d)] = cid
        add({"id": cid, "kind": "configuration", "name": f"{name} ({dname}, Mock et al. 2022)",
             "description": f"{name} as run by the BERTax authors with the {dlabel} dataset's training partition as reference or training data.",
             "status": "needs_review", "facets": {**FACETS, "method_types": mtypes}, "source_ids": [SRC],
             "links": [{"relation": "configuration_of", "target_id": target}],
             "attributes": {"reported_name": name, "foundation_model_eligible": False, "parameters": params,
                            "source_locator": CONFIG_LOCATOR,
                            "access_reuse": "Tool run by the article's authors; trained models and reference builds are not released except the downloadable final BERTax model",
                            "missing_metadata": {"version": {"reason": "unreported", "note": "Tool versions are not stated in the article or SI, except MMseqs2-linclust 11.e1a1c used for dataset clustering"}}}})

# ---------------------------------------------------------------- evaluations and results
EVAL = {}


def evaluation(tool, d, sources, locator):
    eid = f"{P}-eval-{tool}-{d}"
    if eid in EVAL:
        return eid
    EVAL[eid] = True
    add({"id": eid, "kind": "evaluation", "name": f"{TOOLS[tool][0]} on the BERTax {DATASETS[d][1].lower()}",
         "description": "Published taxonomic-classification comparison; transcribed, not reproduced.",
         "status": "needs_review", "facets": FACETS, "source_ids": sources,
         "links": [{"relation": "system", "target_id": CONFIG[(tool, d)]},
                   {"relation": "assessment", "target_id": PROTO[d]},
                   {"relation": "data", "target_id": f"{P}-data-{d}"}],
         "attributes": {"origin": "author_reported", "protocol": PROTO[d], "version": "Primary source as retrieved 2026-10-12",
                        "comparison": {"protocol_id": PROTO[d], "dataset_version": f"BERTax {DATASETS[d][1].lower()} (Mock et al. 2022)",
                                       "split": DATASETS[d][2], "population": DATASETS[d][3],
                                       "inputs": "1,500-nt genome fragments", "adaptation": "Reference or training data restricted to the dataset's training partition",
                                       "metric_implementation": "Top prediction only; unclassified samples treated as random guesses for AveP",
                                       "aggregation": "Macro average over classes for AveP", "budget": None},
                        "source_locator": locator,
                        "limitations": ["All tools were run by the BERTax authors, who developed BERTax; the evaluations are author_reported.",
                                        "Database tools were restricted to the training partition as reference; whole reference genomes were excluded to avoid duplicate samples between training and test data."]}})
    return eid


def result(rid, eid, metric, printed, qualifier, unit, locator, sha, url, src, method, method_note, direction="higher", extra=None):
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
             "numeric_value": printed, "metric_qualifier": qualifier, "source_locator": locator,
             "missing_metadata": {"uncertainty": {"reason": "unreported"}},
             "review": review(method, method_note, sha, url)}
    if extra:
        attrs.update(extra)
    add({"id": rid, "kind": "result", "name": rid.replace(P + "-result-", "bertax "),
         "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
         "status": "needs_review", "facets": {}, "source_ids": [src], "links": [{"relation": "evaluation", "target_id": eid}],
         "attributes": attrs})
    claims_rows.append([rid, src, locator, printed, "result"])


T1_NOTE = "Read from the PDF text layer (pdf.js 4.0.379) of the pinned PNAS PDF; extract/extract_bertax.py asserts the title, column headers, row labels and seven two-decimal values per row."
COL_LABEL = {"closely": "Closely related", "distantly": "Distantly related", "final": "Final"}
RANK_LABEL = {"superkingdom": "Supk.", "phylum": "Phyl.", "genus": "Genus"}
for tool, (label, values) in table1.items():
    for (d, rank), v in zip(T1_COLS, values):
        eid = evaluation(tool, d, [SRC, SRC_PDF, SRC_SI], "Table 1 (PNAS PDF page 4); SI Table S2" if d != "final" else "Table 1 (PNAS PDF page 4)")
        loc = f"Table 1, row \"{label}\", column group \"{COL_LABEL[d]}\", column \"{RANK_LABEL[rank]}\" (PNAS PDF page 4)"
        extra = None
        if tool == "bertax" and d == "final" and rank == "phylum":
            extra = {"source_discrepancy": "Results 'Performance of Final BERTax Model' paragraph 1 prints 95.20% for BERTax phylum prediction on the final dataset; Table 1 and SI Table S7 print 95.10. Table value kept."}
        result(f"{P}-result-{tool}-{d}-{rank}-avep", eid, "macro-average-precision", v,
               f"{rank} rank; macro average over classes; unclassified samples treated as random guesses", "percent",
               loc, PDF_SHA, PDF_URL, SRC_PDF, ["pdf-text-parse"], T1_NOTE, extra=extra)

S2_NOTE = "Read from `pdftotext -layout` output of the pinned SI PDF; extract/extract_bertax.py asserts the caption, the three header lines, the nine tool labels and eight values per row."
for label, tool in S2_LABELS:
    for (d, rank, m), v in zip(S2_COLS, s2[label]):
        eid = evaluation(tool, d, [SRC, SRC_PDF, SRC_SI], "Table 1 (PNAS PDF page 4); SI Table S2")
        loc = f"SI Table S2, row \"{label}\", column group \"{DATASETS[d][0]} dataset\", \"{rank}\", column \"{m}\" (SI page S15)"
        if m == "acc.":
            result(f"{P}-result-{tool}-{d}-{rank}-accuracy", eid, "accuracy", v, f"{rank} rank; SI Table S2 'acc.'", "percent",
                   loc, SI_SHA, SI_URL, SRC_SI, ["pdf-text-parse"], S2_NOTE)
        else:
            result(f"{P}-result-{tool}-{d}-{rank}-proportion-classified", eid, "proportion", v,
                   f"{rank} rank; share of test samples the tool returned a prediction for", "percent",
                   loc, SI_SHA, SI_URL, SRC_SI, ["pdf-text-parse"], S2_NOTE, direction="higher")

S5_NOTE = "Read from `pdftotext -layout` output of the pinned SI PDF; extract/extract_bertax.py asserts the caption, header and the three tool labels with six values each."
S5_QUAL = {"unfiltered": "all distantly related test sequences",
           "filtered": "test sequences without a megablast hit to the training partition",
           "left-out": "test sequences with at least one megablast hit to the training partition (removed by the filter)"}
for label, tool in S5_LABELS:
    for (rank, sub), v in zip(S5_COLS, s5[label]):
        eid = evaluation(tool, "distantly", [SRC, SRC_PDF, SRC_SI], "Table 1 (PNAS PDF page 4); SI Table S2")
        loc = f"SI Table S5, row \"{label}\", column group \"{rank}\", column \"acc. {sub}\" (SI page S16)"
        result(f"{P}-result-{tool}-distantly-{rank}-accuracy-homology-{sub}", eid, "accuracy", v,
               f"{rank} rank; SI Table S5; {S5_QUAL[sub]}", "percent", loc, SI_SHA, SI_URL, SRC_SI, ["pdf-text-parse"], S5_NOTE)

# ---------------------------------------------------------------- descriptive claims
CLAIM_REVIEW = review(["transcription"], "Transcribed from the pinned article XML text.", XML_SHA, XML_URL)
for cid, subject, field, value, loc in [
        ("claim-bertax-training-data", f"{P}-model-bertax", "training_data",
         "Pretrained on about 2.5 million (2,492,474) 1,500-nt fragments from NCBI RefSeq genomes of archaea, bacteria, eukaryotes and viruses, clustered at 80% identity; fine-tuned on phylum classes with at least 10,000 fragments.",
         "Results paragraph 4; Materials and Methods 'Pretraining Dataset', 'Preparing Data for Fine-Tuning'"),
        ("claim-same-reference-data", f"{P}-benchmark", "comparison_design",
         "All methods compared have exactly the same reference or training data as BERTax; whole reference genomes are not included, which the authors call a necessary deviation from the designed use of database methods.",
         "Results 'Comparison to Other Classification Approaches' paragraph 1"),
        ("claim-final-phylum-discrepancy", SRC, "printed_value_conflict",
         "Results 'Performance of Final BERTax Model' prints 95.20% for BERTax phylum AveP on the final dataset; Table 1 and SI Table S7 print 95.10.",
         "Results 'Performance of Final BERTax Model' paragraph 1; Table 1; SI Table S7")]:
    add({"id": f"{P}-{cid}", "kind": "claim", "name": f"{field}: {subject}",
         "description": "Descriptive fact transcribed from the pinned source.", "status": "needs_review", "facets": {},
         "source_ids": [SRC] + ([SRC_PDF, SRC_SI] if "discrepancy" in cid else []),
         "links": [{"relation": "subject", "target_id": subject}],
         "attributes": {"field": field, "value": value, "source_locator": loc, "review": CLAIM_REVIEW}})
    claims_rows.append([f"{P}-{cid}", SRC, loc, value, "claim"])

# ---------------------------------------------------------------- relevance judgements (drafts)
UC = "use-case-diagnostic-dna-pathogen-identification"
JUDGEMENTS = {
    "closely": (1, "Closely related (test genera present in the reference)",
                "Tests whether a trained classifier matches reference-based tools when relatives are in the reference."),
    "distantly": (2, "Distantly related (test genera absent from the reference)",
                  "Tests the use case's question about organisms absent from the reference: every test fragment's genus is missing from the reference and training data."),
    "final": (3, "Final model dataset (larger reference, genus rank added)",
              "Adds genus-level classification with a larger reference, closer to how the released BERTax model is used."),
}
for d, (order, stratum, why) in JUDGEMENTS.items():
    evals = sorted(e for e in EVAL if e.endswith(f"-{d}"))
    jid = f"use-case-mapping-{P}-{d}"
    add({"id": jid, "kind": "claim",
         "name": f"Relevance of the BERTax {DATASETS[d][1].lower()} protocol (Mock et al. 2022) to \"Select a DNA pathogen-identification workflow for diagnostic testing\"",
         "description": f"Machine-learning classifiers (BERTax, DeepMicrobes) and the baseline k-mer and alignment tools Kraken2 and minimap2 are scored on the same fragments with the same reference data. {why} It is proxy evidence: the inputs are simulated genome fragments, not specimen reads, and ranks stop at genus.",
         "status": "needs_review", "facets": {}, "source_ids": [SRC, SRC_PDF, SRC_SI],
         "links": [{"relation": "subject", "target_id": UC}],
         "attributes": {"field": f"links:assessed_by:{PROTO[d]}", "value": PROTO[d], "relevance": "proxy",
                        "endpoint": "Macro AveP" + (", accuracy and proportion classified" if d != "final" else "") + " at superkingdom and phylum" + (" and genus" if d == "final" else "") + " rank on 1,500-nt genome fragments",
                        "rationale": f"Machine-learning classifiers (BERTax, DeepMicrobes) and the baseline k-mer and alignment tools Kraken2 and minimap2 are scored on the same fragments with the same reference data. {why} It is proxy evidence: the inputs are simulated genome fragments, not specimen reads, and ranks stop at genus.",
                        "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                                        "Do not combine these results with another protocol's results; inputs, references and taxonomic ranks differ between sources."],
                        "limitations": ["Simulated 1,500-nt genome fragments from RefSeq genomes; no sequencing errors, host DNA or clinical specimens.",
                                        "Superkingdom, phylum and genus only; pathogen identification usually needs species or strain.",
                                        "Database tools were given only the training partition as reference, not whole genomes, which the authors call a necessary deviation from their designed use.",
                                        "MEGAN-LR, the third named baseline, is not compared.",
                                        "All tools were run by the BERTax authors (author_reported); no uncertainty is printed."],
                        "citation_locators": [{"source_id": SRC_PDF, "locator": "Table 1"},
                                              {"source_id": SRC_SI, "locator": "Tables S2 and S5" if d == "distantly" else ("Table S2" if d == "closely" else "Details to PR-curve plots")},
                                              {"source_id": SRC, "locator": "Materials and Methods 'Three Evaluation Datasets', 'Comparison to Other Tools'"}],
                        "source_locator": f"{SRC_PDF}: Table 1; {SRC_SI}: Tables S2 and S5; {SRC}: Materials and Methods",
                        "revision": 1,
                        "reason": "Drafted by the extracting agent in the 2026-10-12 ML-versus-baseline pass (issue #121; data/omics/use-case-coverage-dna-pathogen-20261012-bertax). Not reviewed.",
                        "comparison_group": "bertax2022-fragments", "comparison_title": "BERTax genome-fragment classification against database tools (Mock et al. 2022)",
                        "headline_metric": "macro-average-precision", "stratum_label": stratum, "stratum_order": order,
                        "review": review(["scope-review"], "Judgement drafted by the extracting agent from the pinned article and SI.", PDF_SHA, PDF_URL)}})

assert len({r["id"] for r in records}) == len(records)
with open(f"{out_dir}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in sorted(records, key=lambda r: r["id"]):
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(f"{out_dir}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
from collections import Counter
print(Counter(r["kind"] for r in records))
