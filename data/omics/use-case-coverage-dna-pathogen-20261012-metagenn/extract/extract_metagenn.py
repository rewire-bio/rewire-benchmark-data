"""Extract the MetageNN (Moreno et al., BMC Bioinformatics 2024) method comparison into batch records.

Input (pinned, passed as an argument): the Europe PMC full-text XML of PMC11022314
(sha256 ac4b137508d295d5e04e9be263bef40bdcf2c494e096407e5896611194f14e12), and the batch folder.

Table 1 is parsed from its <table-wrap>; the other values are printed in the Results prose (the
accuracy results are otherwise shown only in Figures 3 and 4, which are not read). Every row label,
header and quoted sentence is asserted before a value is written. Run with python3 -I.
"""
import csv
import hashlib
import html
import json
import re
import sys
from collections import Counter

xml_path, out_dir = sys.argv[1:3]
raw = open(xml_path, "rb").read()
SHA = "ac4b137508d295d5e04e9be263bef40bdcf2c494e096407e5896611194f14e12"
assert hashlib.sha256(raw).hexdigest() == SHA
xml = raw.decode("utf-8")
DATE = "2026-10-12"
P = "dna-pathogen-20261012-metagenn"
SRC = f"{P}-source"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11022314/fullTextXML"
FACETS = {"areas": ["microbes-communities"], "contexts": ["research"]}
REVIEWER_NOTE = ("Extracting Claude agent for the 2026-10-12 ML-versus-baseline pass (issue #121); "
                 "extraction only, not a review. Pending an independent review-evidence pass.")
records, claims_rows = [], []


def text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).replace(" ,", ",").strip()


def add(record):
    records.append(record)
    return record


def review(method, note):
    return {"method": method, "method_note": note, "reviewer": ["claude"], "reviewer_note": REVIEWER_NOTE,
            "date": DATE, "artifact_sha256": SHA, "retrieval_url": URL,
            "note": "Extracted, not reviewed. The review-evidence pass must re-check this value against the pinned artifact."}


body = text(re.search(r"<body>.*</body>", xml, re.S).group(0))

# ---------------------------------------------------------------- Table 1
tw = re.search(r'<table-wrap id="Tab1".*?</table-wrap>', xml, re.S).group(0)
rows = [[text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)] for tr in re.findall(r"<tr>.*?</tr>", tw, re.S)]
assert text(re.search(r"<caption>(.*?)</caption>", tw, re.S).group(1)) == "Memory requirements for database storage and speed for each method on ONT data"
assert rows[0] == ["Method", "Memory (GB)", "Speed (reads/sec)"], rows[0]
T1_TOOLS = ["MetageNN", "GeNet", "Kraken2", "MetaMaps", "MEGAN-LR", "MMseqs2"]
assert [r[0] for r in rows[1:]] == T1_TOOLS, rows
table1 = {r[0]: (r[1], r[2]) for r in rows[1:]}
assert table1["Kraken2"] == ("3.7", "13.471")


def quote(sentence):
    assert sentence in body, sentence
    return sentence


S_ALL = quote("For F1 and sensitivity scores, MMseqs2 achieved the highest average with 0.85 and 0.81, respectively, followed by Kraken2 with 0.83 and 0.79, respectively.")
S_OUT = quote("MetageNN again achieved the best results, having the highest F1 and sensitivity scores of 0.88 and 0.87, respectively")
S_READS = quote("Here, MetageNN outperformed all existing tools classifying 93.26% of the reads from species out of the database at the genus level. This result was followed by MMseqs2, Kraken2, MEGAN-LR and MetaMaps with 85.49%, 64.90%, 53.06% and 37.30%, respectively.")
S_SPEED = quote("Kraken2, including its database loading time, delivers the highest number of reads processed per second, with 13,471 reads per second.")
S_FOUR_CPU = quote("We allowed four CPUs to be used by all tools as a representative of a commonly available system.")

# ---------------------------------------------------------------- source
add({"id": SRC, "kind": "source",
     "name": "MetageNN: a memory-efficient neural network taxonomic classifier robust to sequencing errors and missing genomes",
     "description": "Primary source retrieved and hashed for the 2026-10-12 ML-versus-baseline pass.",
     "status": "needs_review", "facets": FACETS, "source_ids": [], "links": [],
     "attributes": {"url": "https://doi.org/10.1186/s12859-024-05760-3", "artifact_url": URL,
                    "version": "BMC Bioinformatics 25:153, published 2024-04-16; PMC11022314 full-text XML",
                    "retrieved_at": "2026-10-12T20:50:20Z", "artifact_sha256": SHA,
                    "doi": "10.1186/s12859-024-05760-3", "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
                    "media_type": "application/xml", "venue": "BMC Bioinformatics", "year": 2024,
                    "source_locator": "Licence statement in the article XML <license> element: Creative Commons Attribution 4.0"}})

# ---------------------------------------------------------------- systems
add({"id": f"{P}-model-metagenn", "kind": "model", "name": "MetageNN",
     "description": "Feed-forward neural network on 6-mer profiles of 1 kbp sequences sampled from reference genomes; long reads are split into 1 kbp chunks and classified by majority vote at genus level.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["supervised_machine_learning"]}, "source_ids": [SRC], "links": [],
     "attributes": {"reported_name": "MetageNN", "entity_level": "family",
                    "source_locator": "Background paragraph 4; Results 'MetageNN presents a higher F1 score than GeNet...' Experimental setup; Fig. 5 caption",
                    "access": "Code and genome lists at https://github.com/csb5/MetageNN (no licence file; not pinned in this pass)",
                    "training_data": "Main database: 516 RefSeq genomes (505 species, 311 genera); training set of about 17 million 1 kbp sequences at 8x coverage",
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the evaluated model is the configuration"}}}})
add({"id": f"{P}-model-genet", "kind": "model", "name": "GeNet",
     "description": "Convolutional (ResNet) taxonomic classifier with one-hot and positional embeddings of a fixed-length read.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["supervised_machine_learning"]}, "source_ids": [SRC], "links": [],
     "attributes": {"reported_name": "GeNet", "entity_level": "family",
                    "source_locator": "Results 'MetageNN is more effective and robust...' Baselines paragraph 1",
                    "missing_metadata": {"version": {"reason": "unreported"}}}})
add({"id": f"{P}-method-metamaps", "kind": "method", "name": "MetaMaps",
     "description": "Alignment-based long-read taxonomic classifier.",
     "status": "needs_review", "facets": {**FACETS, "method_types": ["conventional_pipeline"]}, "source_ids": [SRC], "links": [],
     "attributes": {"reported_name": "MetaMaps", "entity_level": "method",
                    "source_locator": "Results 'MetageNN presents a higher F1 score than GeNet...' Baselines paragraph 1",
                    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}})

TOOLS = {
    "metagenn": ("MetageNN", f"{P}-model-metagenn", ["supervised_machine_learning"],
                 "Main-database model (capacity about doubled from the small-database model), trained 3 days on four GPUs with early stopping; reads segmented into non-overlapping 1 kbp chunks, majority vote, classified if probability >= 0.5"),
    "genet": ("GeNet", f"{P}-model-genet", ["supervised_machine_learning"],
              "Extended to a capacity similar to MetageNN and trained on the same main-database training set; majority vote and 0.5 probability cutoff"),
    "kraken2": ("Kraken2", "catalog-model-kraken2", ["conventional_pipeline"], "Index built from the main-database genomes; default settings"),
    "metamaps": ("MetaMaps", f"{P}-method-metamaps", ["conventional_pipeline"], "Index built from the main-database genomes; default settings"),
    "megan-lr": ("MEGAN-LR", "dna-pathogen-20261009-method-megan-lr", ["conventional_pipeline"],
                 "MEGAN-LR on minimap2 nucleotide alignments to the main-database genomes (MEGAN-LR-nuc in Portik et al. 2022); default settings"),
    "mmseqs2": ("MMseqs2", "discovery-model-mmseqs2", ["conventional_pipeline"], "Nucleotide database built from the main-database genomes; default settings"),
}
CONFIG = {}
for tool, (name, target, mtypes, params) in TOOLS.items():
    cid = f"{P}-config-{tool}"
    CONFIG[tool] = cid
    add({"id": cid, "kind": "configuration", "name": f"{name} (main database, Moreno et al. 2024)",
         "description": f"{name} as run by the MetageNN authors with the 516-genome main database.",
         "status": "needs_review", "facets": {**FACETS, "method_types": mtypes}, "source_ids": [SRC],
         "links": [{"relation": "configuration_of", "target_id": target}],
         "attributes": {"reported_name": name, "foundation_model_eligible": False, "parameters": params,
                        "source_locator": "Results 'MetageNN presents a higher F1 score than GeNet...' Baselines and Experimental setup; Methods 'Databases'",
                        "access_reuse": "Tool run by the article's authors; the trained MetageNN model is not linked from the article",
                        "missing_metadata": {"version": {"reason": "unreported", "note": "No tool versions are given"}}}})

# ---------------------------------------------------------------- data, benchmark, protocols
add({"id": f"{P}-data-isolates", "kind": "dataset", "name": "ONT reads from 81 bacterial isolates (Moreno et al. 2024)",
     "description": "ONT R9.4.1 reads from NCBI SRA for 81 bacterial strains with verified RefSeq genomes (assembly ANI > 99%), subsampled to about 20,000 reads per isolate.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
     "attributes": {"version": "As described in Moreno et al. 2024; SRA run lists in the authors' repository",
                    "population": "47 isolates whose species genome is in the main database ('Species in the database') and 34 whose genome is not ('Species out of the database')",
                    "split": "Two test datasets by database membership; MetageNN trained only on reference genomes",
                    "access": "SRA run IDs listed at https://github.com/csb5/MetageNN (data/list_of_sra_ids_species_in.txt and _out.txt)",
                    "source_locator": "Methods 'Data' and 'Databases'"}})
add({"id": f"{P}-data-mocks", "kind": "dataset", "name": "30 ONT pseudo-mock communities of out-of-database species (Moreno et al. 2024)",
     "description": "Pseudo-mock communities built from the isolate reads of species out of the database, 20 to 34 species each, up to 100,000 reads log-distributed across species.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
     "attributes": {"version": "'Mock - Species out of DB' as described in Moreno et al. 2024",
                    "population": "30 pseudo-mock communities", "split": "Test only",
                    "access": "Not released; built from the listed SRA runs",
                    "source_locator": "Results 'MetageNN is more sensitive ... at the community-level for ONT pseudo-mock communities' Experimental setup"}})
add({"id": f"{P}-benchmark", "kind": "benchmark", "name": "MetageNN long-read genus classification benchmark (Moreno et al. 2024)",
     "description": "Genus-level classification of ONT reads from bacterial isolates and pseudo-mock communities, with every tool using the same 516-genome database.",
     "status": "needs_review", "facets": FACETS, "source_ids": [SRC], "links": [],
     "attributes": {"entity_level": "suite", "version": "BMC Bioinformatics 2024, Table 1 and Results prose",
                    "task": "Assign ONT reads to their genus with or without the species genome in the reference",
                    "source_locator": "Results; Methods 'Data' and 'Databases'",
                    "scope_note": "Per-tool sensitivity, precision and F1 are shown only in Figures 3 and 4 (bar plots with values drawn on the figure) and were not read. Only values printed in the text and Table 1 are extracted. Figure 2 (GeNet and DeepMicrobes against MetageNN on the 47-genome small database) is not a baseline comparison and was not extracted.",
                    "limitations": ["The authors developed MetageNN and ran every tool.",
                                    "The reference holds 516 genomes, far smaller than the databases clinical classifiers use.",
                                    "Genus level only; isolates from bacteria only."]}})
PROTOS = {
    "isolates": ("Genus-level read classification of ONT bacterial isolates, main database (Moreno et al. 2024)",
                 "Per-isolate sensitivity, precision and F1 of read assignments at genus level, averaged across isolates; reported for all isolates, species in the database and species out of the database, and by number of species per genus.",
                 f"{P}-data-isolates", "Results 'Evaluation metrics'; 'Results for all genomes'; 'Results for “Species out of the database” settings'",
                 "For each taxon, sensitivity is the proportion of its reads classified as such and precision the proportion of correctly classified reads; F1 is their harmonic mean. Averages are across bacterial isolates; Wilcoxon rank-sum tests compare MetageNN with each tool.",
                 "Test sets 'Species in the database' (47 isolates) and 'Species out of the database' (34 isolates)", "81 ONT bacterial isolates, about 20,000 reads each"),
    "mocks": ("Read classification on 30 ONT pseudo-mock communities of out-of-database species (Moreno et al. 2024)",
              "Average percentage of reads classified at genus level per tool across the 30 pseudo-mocks; community-level sensitivity, precision and F1 at 0.001, 0.1 and 1% thresholds appear only in Figure 4b.",
              f"{P}-data-mocks", "Results 'Read classification results'; 'Community-level results'",
              "Read classification: percentage of reads assigned at genus level, whether or not correctly. Community level: presence of a genus above a cumulative read-count threshold.",
              "Test only", "30 pseudo-mocks of 20 to 34 out-of-database species, up to 100,000 reads each"),
    "resources": ("Database storage and classification speed on ONT data, main database (Moreno et al. 2024)",
                  "Memory needed to store each tool's database or model weights, and reads classified per second with four CPUs.",
                  f"{P}-data-isolates", "Table 1; Results 'MetageNN is faster and requires less storage than alignment and k-mer-based tools, respectively'",
                  "Speed includes database loading (Kraken2) and k-mer counting and dataset loading (MetageNN); four CPUs for all tools.",
                  "Not stated", "ONT reads (the timed read set is not stated)"),
}
for key, (name, desc, data, loc, definition, *_) in PROTOS.items():
    add({"id": f"{P}-protocol-{key}", "kind": "protocol", "name": name, "description": desc, "status": "needs_review",
         "facets": FACETS, "source_ids": [SRC],
         "links": [{"relation": "uses_data", "target_id": data}, {"relation": "part_of", "target_id": f"{P}-benchmark"}],
         "attributes": {"protocol": desc, "version": "BMC Bioinformatics 2024", "metric_definition": definition, "source_locator": loc,
                        "limitations": (["The article does not say which ONT reads were timed; the dataset link is the isolate set."] if key == "resources" else
                                        ["Reads classified is not accuracy: a classified read may be assigned to the wrong genus."] if key == "mocks" else
                                        ["Most per-tool values are only in Figure 3; the text prints a few averages."])}})

EVAL = {}


def evaluation(tool, proto):
    eid = f"{P}-eval-{tool}-{proto}"
    if eid not in EVAL:
        EVAL[eid] = proto
        add({"id": eid, "kind": "evaluation", "name": f"{TOOLS[tool][0]} on {PROTOS[proto][0][0].lower() + PROTOS[proto][0][1:]}",
             "description": "Published long-read classification comparison; transcribed, not reproduced.",
             "status": "needs_review", "facets": FACETS, "source_ids": [SRC],
             "links": [{"relation": "system", "target_id": CONFIG[tool]}, {"relation": "assessment", "target_id": f"{P}-protocol-{proto}"},
                       {"relation": "data", "target_id": PROTOS[proto][2]}],
             "attributes": {"origin": "author_reported", "protocol": f"{P}-protocol-{proto}", "version": "Primary source as retrieved 2026-10-12",
                            "comparison": {"protocol_id": f"{P}-protocol-{proto}", "dataset_version": PROTOS[proto][0],
                                           "split": PROTOS[proto][5], "population": PROTOS[proto][6], "inputs": "ONT R9.4.1 reads",
                                           "adaptation": "All tools use the 516-genome main database", "metric_implementation": PROTOS[proto][4],
                                           "aggregation": "Mean across isolates" if proto == "isolates" else ("Mean across 30 pseudo-mocks" if proto == "mocks" else None),
                                           "budget": "Four CPUs" if proto == "resources" else None},
                            "source_locator": PROTOS[proto][3],
                            "limitations": ["All tools were run by the MetageNN authors (author_reported)."]}})
    return eid


def result(rid, tool, proto, metric, printed, numeric, qualifier, unit, locator, method, note, direction="higher", extra=None):
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed,
             "metric_qualifier": qualifier, "source_locator": locator,
             "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Figure 3 shows standard-deviation error bars; no value is printed in the text"} if proto == "isolates" else {"reason": "unreported"}},
             "review": review(method, note)}
    if numeric is None:
        attrs["numeric_value"] = None  # '13.471' conflicts with the text's 13,471; see source_discrepancy
    else:
        attrs["numeric_value"] = numeric
    if extra:
        attrs.update(extra)
    add({"id": rid, "kind": "result", "name": rid.replace(P + "-result-", "metagenn "),
         "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
         "status": "needs_review", "facets": {}, "source_ids": [SRC],
         "links": [{"relation": "evaluation", "target_id": evaluation(tool, proto)}], "attributes": attrs})
    claims_rows.append([rid, SRC, locator, printed, "result"])


T1_NOTE = "Parsed from the Table 1 <table-wrap> of the pinned XML by extract/extract_metagenn.py, with caption, header and the six method labels asserted."
PROSE_NOTE = "Transcribed from a Results sentence of the pinned XML; extract/extract_metagenn.py asserts the exact sentence before writing the value."
T1_ID = {"MetageNN": "metagenn", "GeNet": "genet", "Kraken2": "kraken2", "MetaMaps": "metamaps", "MEGAN-LR": "megan-lr", "MMseqs2": "mmseqs2"}
for label, (mem, speed) in table1.items():
    tool = T1_ID[label]
    result(f"{P}-result-{tool}-resources-storage", tool, "resources", "reference-storage-size", mem, mem,
           "database or index (model weights for MetageNN and GeNet) built from the 516-genome main database", "gigabyte",
           f"Table 1, row \"{label}\", column \"Memory (GB)\"", ["deterministic-table-parse"], T1_NOTE, direction="lower")
    conflict = label == "Kraken2"
    result(f"{P}-result-{tool}-resources-speed", tool, "resources", "inference-throughput", speed, None if conflict else speed,
           "reads classified per second with four CPUs", "sample-per-second",
           f"Table 1, row \"{label}\", column \"Speed (reads/sec)\"", ["deterministic-table-parse"], T1_NOTE,
           extra={"unit_detail": "ONT reads per second", **({"source_discrepancy": "Table 1 prints '13.471' reads/sec, but the Results text prints 13,471 reads per second for Kraken2 and calls it the fastest tool (recorded as a separate result); numeric_value is left null."} if conflict else {})})
result(f"{P}-result-kraken2-resources-speed-text", "kraken2", "resources", "inference-throughput", "13,471", "13471",
       "reads classified per second with four CPUs, including database loading time; value printed in the text", "sample-per-second",
       "Results 'MetageNN is faster and requires less storage than alignment and k-mer-based tools, respectively' paragraph 3, sentence 4",
       ["transcription"], PROSE_NOTE, extra={"unit_detail": "ONT reads per second",
                                            "source_discrepancy": "Table 1 prints this cell as '13.471' reads/sec."})

ALL_LOC = "Results 'Results for all genomes' paragraph 1, sentence 3 (values shown in Fig. 3a)"
for tool, f1, sens in [("mmseqs2", "0.85", "0.81"), ("kraken2", "0.83", "0.79")]:
    q = "genus level; mean across all 81 isolates (species in and out of the database)"
    result(f"{P}-result-{tool}-isolates-all-f1", tool, "isolates", "f1-score", f1, f1, q, "fraction", ALL_LOC, ["transcription"], PROSE_NOTE)
    result(f"{P}-result-{tool}-isolates-all-recall", tool, "isolates", "recall", sens, sens, q, "fraction", ALL_LOC, ["transcription"], PROSE_NOTE)
OUT_LOC = "Results 'Results for “Species out of the database” settings' paragraph 3, last sentences (values shown in Fig. 3f)"
q = "genus level; mean across the out-of-database isolates whose genus has more than three species"
result(f"{P}-result-metagenn-isolates-out-gt3-f1", "metagenn", "isolates", "f1-score", "0.88", "0.88", q, "fraction", OUT_LOC, ["transcription"], PROSE_NOTE)
result(f"{P}-result-metagenn-isolates-out-gt3-recall", "metagenn", "isolates", "recall", "0.87", "0.87", q, "fraction", OUT_LOC, ["transcription"], PROSE_NOTE)
READS_LOC = "Results 'Read classification results' paragraph 1 (values shown in Fig. 4a)"
for tool, v in [("metagenn", "93.26%"), ("mmseqs2", "85.49%"), ("kraken2", "64.90%"), ("megan-lr", "53.06%"), ("metamaps", "37.30%")]:
    result(f"{P}-result-{tool}-mocks-reads-classified", tool, "mocks", "proportion", v, v.rstrip("%"),
           "share of reads assigned at genus level (correct or not); mean across 30 pseudo-mock communities of out-of-database species",
           "percent", READS_LOC, ["transcription"], PROSE_NOTE)

# ---------------------------------------------------------------- claims
CR = review(["transcription"], "Transcribed from the pinned article XML text.")
for cid, subject, field, value, loc in [
        ("claim-same-database", f"{P}-benchmark", "comparison_design",
         "All baselines used the same database of genomes; the non-machine-learning tools' indices were built from the main-database genomes and run with default settings.",
         "Methods 'Databases' paragraph 1; Results 'MetageNN presents a higher F1 score than GeNet...' Experimental setup"),
        ("claim-in-database-ranking", f"{P}-protocol-isolates", "reported_ranking",
         "For species in the database, Kraken2, MetaMaps and MEGAN-LR had the best average F1, sensitivity and precision, outperforming MetageNN (values in Fig. 3b only).",
         "Results 'Results for “Species in the database” settings' paragraph 1"),
        ("claim-out-of-database-ranking", f"{P}-protocol-isolates", "reported_ranking",
         "For species out of the database, MetageNN had the highest sensitivity along with MMseqs2, significantly above MetaMaps, Kraken2, GeNet and MEGAN-LR; its precision was slightly lower than MetaMaps, Kraken2 and MMseqs2 (values in Fig. 3c only).",
         "Results 'Results for “Species out of the database” settings' paragraph 2")]:
    add({"id": f"{P}-{cid}", "kind": "claim", "name": f"{field}: {subject}", "description": "Descriptive fact transcribed from the pinned source.",
         "status": "needs_review", "facets": {}, "source_ids": [SRC], "links": [{"relation": "subject", "target_id": subject}],
         "attributes": {"field": field, "value": value, "source_locator": loc, "review": CR}})
    claims_rows.append([f"{P}-{cid}", SRC, loc, value, "claim"])

# ---------------------------------------------------------------- relevance judgements (drafts)
UC = "use-case-diagnostic-dna-pathogen-identification"
J = {
    "isolates": (1, "ONT bacterial isolates", "recall",
                 "Kraken2 and MMseqs2 are scored on real ONT reads at genus level. The only printed MetageNN values are for out-of-database isolates in genera with more than three species, so no printed value compares MetageNN with a baseline on the same subset; the full comparison is in Figure 3 only.",
                 "Genus-level sensitivity and F1 of read assignment, averaged across ONT bacterial isolates"),
    "mocks": (2, "Pseudo-mock communities of out-of-database species", "proportion",
              "MetageNN and the baselines Kraken2 and MEGAN-LR (on minimap2 alignments) are run on the same reads from species missing from the reference, which bears on the use case's question about organisms absent from the reference. The printed endpoint is the share of reads classified, not whether they were classified correctly.",
              "Share of reads assigned at genus level across 30 pseudo-mocks of out-of-database species"),
}
for key, (order, stratum, headline, why, endpoint) in J.items():
    jid = f"use-case-mapping-{P}-{key}"
    rationale = why + " It is proxy evidence: isolate-derived reads, a 516-genome reference and genus-level calls, not patient specimens."
    add({"id": jid, "kind": "claim",
         "name": f"Relevance of {PROTOS[key][0][0].lower() + PROTOS[key][0][1:]} to \"Select a DNA pathogen-identification workflow for diagnostic testing\"",
         "description": rationale, "status": "needs_review", "facets": {}, "source_ids": [SRC],
         "links": [{"relation": "subject", "target_id": UC}],
         "attributes": {"field": f"links:assessed_by:{P}-protocol-{key}", "value": f"{P}-protocol-{key}", "relevance": "proxy",
                        "endpoint": endpoint, "rationale": rationale,
                        "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                                        "Do not combine these results with another protocol's results; references and taxonomic ranks differ between sources."],
                        "limitations": ["Most per-tool accuracy values are only in Figures 3 and 4 and were not extracted.",
                                        "Bacterial isolates only; no host DNA, viruses, fungi or clinical specimens.",
                                        "A 516-genome reference and genus-level classification.",
                                        "minimap2 is used only to produce MEGAN-LR's alignments, not scored on its own.",
                                        "All tools were run by the MetageNN authors (author_reported); no uncertainty is printed."],
                        "citation_locators": [{"source_id": SRC, "locator": PROTOS[key][3]}],
                        "source_locator": f"{SRC}: {PROTOS[key][3]}", "revision": 1,
                        "reason": "Drafted by the extracting agent in the 2026-10-12 ML-versus-baseline pass (issue #121; data/omics/use-case-coverage-dna-pathogen-20261012-metagenn). Not reviewed.",
                        "comparison_group": "metagenn2024-ont", "comparison_title": "MetageNN against alignment and k-mer classifiers on ONT reads (Moreno et al. 2024)",
                        "headline_metric": headline, "stratum_label": stratum, "stratum_order": order,
                        "review": review(["scope-review"], "Judgement drafted by the extracting agent from the pinned article.")}})

assert len({r["id"] for r in records}) == len(records)
with open(f"{out_dir}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in sorted(records, key=lambda r: r["id"]):
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(f"{out_dir}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
print(Counter(r["kind"] for r in records))
