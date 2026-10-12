"""Extract Fortier, Rudy and Scherer 2026 (PLOS One 21(5):e0348885) Tables 1 to 6 into batch records.

Usage: python3 -I extract_fortier2026.py <PMC13170886 fullTextXML> <batch folder>
Parses the six benchmark tables from the pinned Europe PMC article XML, asserts captions, headers and row labels,
and writes needs_review records. Tables 7 and 8 compare the reimplementations with SpliceAI scores (agreement,
not accuracy against a truth set) and are not extracted.
"""
import json, os, sys
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalize_review, judgement, refresh_coverage, sha256

XML, OUT = sys.argv[1], sys.argv[2]
SHA = "dffe74cee7782cbdfdbc9423cf00f0a846b3d720b90b10e9732d6f768c485176"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13170886/fullTextXML"
assert sha256(XML) == SHA

P = "rna-splicing-20261011-fortier2026"
b = Batch(OUT, P, areas=["dna-genomes"])
SRC = P + "-source-article"
UC = "use-case-patient-rna-splicing-validation"
UC_NAME = "Select a patient-RNA splicing-variant validation workflow"

b.source(SRC, "Analyzing the performance of deep learning splice prediction algorithms (Fortier, Rudy and Scherer, PLOS One 2026)", {
    "url": "https://doi.org/10.1371/journal.pone.0348885",
    "artifact_url": URL,
    "version": "PLOS One 21(5):e0348885, published 2026-05-13; PMC13170886 full-text XML",
    "retrieved_at": "2026-10-11T21:37:04Z",
    "artifact_sha256": SHA,
    "doi": "10.1371/journal.pone.0348885",
    "publication_status": "peer_reviewed",
    "licence": "CC-BY-4.0",
    "media_type": "application/xml",
    "limitations": [
        "All authors are employees of Golden Helix, whose VarSeq software supplies the four legacy algorithms in the Legacy Ensemble (Funding Statement).",
        "Results 'SPiP benchmark results' give OpenSpliceAI balanced accuracy 0.787; Table 3 prints 0.797.",
        "Results 'Riepe benchmark results' give SpliceAI 'balanced accuracy (and F1 score) at 0.839 and 0.836 respectively'; Table 2 prints F1 0.839 and balanced accuracy 0.836.",
        "Methods 'Performance benchmarking methodology' says the algorithms were evaluated across three datasets; six are reported.",
        "A preprint version (bioRxiv 10.1101/2025.11.20.689501, posted 2025-11-20) exists; only the published article was read.",
        # review correction 4
        "The Discussion says SPiP results hold 'even with optimized thresholds'; Methods and Results use the standard 0.5 threshold for SPiP.",
    ],
})

root = ET.parse(XML).getroot()
def txt(e): return " ".join("".join(e.itertext()).split())
TABLES = {}
for tw in root.iter("table-wrap"):
    TABLES[tw.get("id")] = tw

HEAD = ["Method", "Sensitivity", "Specificity", "F1", "Balanced Accuracy"]
ROWS = ["SpliceAI", "CI-SpliceAI", "OpenSpliceAI", "Legacy Ensemble"]
METRICS = [("recall", "Sensitivity"), ("specificity", "Specificity"), ("f1-score", "F1"), ("balanced-accuracy", "Balanced Accuracy")]

BENCH = [  # table id, caption start, key, dataset name, dataset population, protocol text, threshold qualifier, judged, locator
    ("pone.0348885.t001", "Performance metrics for CI-SpliceAI benchmark.", "ci-spliceai-benchmark",
     "CI-SpliceAI benchmark variant set (1,316 variants)",
     "1,316 unique GRCh37 variants with functionally validated splicing impact from the literature, published by the CI-SpliceAI authors; balanced between splice-altering and non-altering variants and between strands; 25.1% alter canonical splice-site dinucleotides",
     "Binary classification of splice-altering versus non-altering variants; maximum of the four SpliceAI-type delta scores above 0.5 is positive; Legacy Ensemble vote N > 1.",
     "maximum delta score > 0.5 (Legacy Ensemble N > 1)", True,
     "Methods 'CI-SpliceAI benchmark dataset'; Table 1"),
    ("pone.0348885.t002", "Performance metrics for Riepe benchmark.", "riepe",
     "Riepe et al. functional splice assay variants (213 variants, ABCA4 and MYBPC3)",
     "152 ABCA4 and 61 MYBPC3 variants from the functional splice assays of Riepe et al. (2021); 81 ABCA4 variants are deep intronic; none alter canonical splice-site dinucleotides",
     "The delta score matching each variant's effect type is used; thresholds are optimised per gene and algorithm for the highest accuracy (an upper-bound estimate); Legacy Ensemble vote N > 1, and N > 2 for ABCA4.",
     "threshold optimised per gene and algorithm for maximum accuracy (upper bound)", True,
     "Methods 'Riepe benchmark dataset' and 'Splice prediction tools'; Table 2"),
    ("pone.0348885.t003", "Performance metrics for SPiP benchmark dataset.", "spip",
     "SPiP benchmark variant set (99,601 variants)",
     "4,616 experimentally characterised variants from 227 genes (1,924 spliceogenic by RT-PCR, Sanger sequencing of RT-PCR products or minigene assays) plus 95,000 common control variants (MAF > 5%) from Leman et al.; 15 variants excluded on conversion to GRCh38, leaving 99,601; about 2% spliceogenic",
     "Binary classification using the authors' class_splice labels; maximum delta score above the standard 0.5 threshold is positive; Legacy Ensemble vote N > 1.",
     "maximum delta score > 0.5 (Legacy Ensemble N > 1)", True,
     "Methods 'SPiP benchmark dataset'; Results 'SPiP benchmark results'; Table 3"),
    ("pone.0348885.t004", "Performance metrics for Barbosa deep intronic benchmark using optimized thresholds.", "barbosa-deep-intronic",
     "Barbosa et al. deep intronic pathogenic variants with matched common controls (484 variants)",
     "242 pathogenic intronic variants more than 10 bp from the nearest splice site with experimental evidence of aberrant splicing (RT-PCR, cDNA sequencing, RNA-seq or minigene), 194 causing pseudoexon activation; 242 matched common gnomAD v2.1 intronic negatives (AF > 1%) from the same genes, absent from ClinVar",
     "Maximum delta score with thresholds optimised for balanced accuracy on this dataset (SpliceAI 0.04, CI-SpliceAI and OpenSpliceAI 0.01); Legacy Ensemble vote N > 0.",
     "threshold optimised per algorithm for balanced accuracy on this dataset", True,
     "Methods 'Barbosa deep intronic benchmark dataset'; Results 'Barbosa deep intronic benchmark results'; Table 4"),
    ("pone.0348885.t005", "Performance metrics for Barbosa ClinVar benchmark.", "barbosa-clinvar",
     "Barbosa et al. ClinVar intronic SNV benchmark (53,600 variants)",
     "53,600 GRCh37 intronic SNVs from ClinVar (release 2022-04) with at least one-star review; pathogenic or likely pathogenic as positive, benign or likely benign as negative; 22.8% alter canonical dinucleotides",
     "Clinical classification as the label; maximum delta score above 0.5 is positive; Legacy Ensemble vote N > 1.",
     "maximum delta score > 0.5 (Legacy Ensemble N > 1)", False,
     "Methods 'Barbosa ClinVar benchmark dataset'; Table 5"),
    ("pone.0348885.t006", "Performance metrics for ClinVar benchmark.", "extended-clinvar",
     "Extended ClinVar benchmark (58,064 variants)",
     "GRCh38 ClinVar Assessments variants (release 2025-10) pre-filtered in VarSeq to those where at least one legacy algorithm predicts a splice effect; positives are pathogenic with 'splice' in the interpretation text, negatives benign; 17.4% alter canonical dinucleotides",
     "Clinical classification as the label after legacy-tool pre-filtering; maximum delta score classification; Legacy Ensemble vote N > 1.",
     "maximum delta score classification after legacy-tool pre-filtering (threshold not restated for this dataset)", False,
     "Methods 'Extended ClinVar benchmark dataset'; Table 6"),
]

MODELS = {
    "openspliceai": ("OpenSpliceAI", "PyTorch reimplementation of SpliceAI retrained on RefSeq MANE v1.3 protein-coding transcripts (GRCh38)."),
    "ci-spliceai": ("CI-SpliceAI", "SpliceAI reimplementation retrained on a collapsed isoform set of manually curated GENCODE HAVANA splice sites from all chromosomes."),
}
SYSTEM = {"SpliceAI": "catalog-model-spliceai"}
for key, (name, desc) in MODELS.items():
    SYSTEM[name] = b.rid("model", key)
    b.entity("model", SYSTEM[name], name, desc, [SRC], {
        "reported_name": name, "entity_level": "family",
        "source_locator": "Introduction paragraph 5; Methods 'Splice prediction tools' and 'Technical overview of deep learning methods'",
        "missing_metadata": {"version": {"reason": "unreported", "note": "Release or checkpoint not printed"}},
    }, method_types=["supervised_machine_learning"])
SYSTEM["Legacy Ensemble"] = b.rid("method", "legacy-ensemble")
b.entity("method", SYSTEM["Legacy Ensemble"], "Legacy Ensemble (N-of-4 vote, VarSeq)",
         "Vote across MaxEntScan, NNSplice, GeneSplicer and a SpliceSiteFinder-style position weight matrix as provided by VarSeq.",
         [SRC], {"reported_name": "Legacy Ensemble", "entity_level": "method",
                 "source_locator": "Methods 'Splice prediction tools' (list item 4 and following paragraph)",
                 "missing_metadata": {"version": {"reason": "unreported", "note": "VarSeq release not printed"}}},
         method_types=["conventional_pipeline"])

CONFIG = {}
CFG_DEF = {
    "SpliceAI": ("spliceai", "Original SpliceAI (TensorFlow/Keras, GENCODE v24 GRCh37 training) run by the authors", ["supervised_machine_learning"]),
    "CI-SpliceAI": ("ci-spliceai", "CI-SpliceAI run by the authors", ["supervised_machine_learning"]),
    "OpenSpliceAI": ("openspliceai", "OpenSpliceAI run by the authors", ["supervised_machine_learning"]),
    "Legacy Ensemble": ("legacy-ensemble", "N-of-4 vote of VarSeq legacy algorithms; the voting threshold giving the highest balanced accuracy was used", ["conventional_pipeline"]),
}
for name, (key, desc, mt) in CFG_DEF.items():
    CONFIG[name] = b.rid("config", key)
    params = ("Masking enabled; maximum distance between variant and gained or lost splice site 500 bp; classification on the maximum of the four delta scores (threshold per benchmark, see evaluations)"
              if name != "Legacy Ensemble" else "Vote threshold N > 1, except N > 0 for the Barbosa deep intronic set and N > 2 for ABCA4 in the Riepe set")
    b.entity("configuration", CONFIG[name], f"{name} (Fortier et al. 2026)", desc, [SRC], {
        "reported_name": name, "foundation_model_eligible": False, "parameters": params,
        "access_reuse": ("SpliceAI weights and precomputed scores are licensed for academic, non-commercial use (Introduction paragraph 4)" if name == "SpliceAI"
                         else "Open-source reimplementation (Introduction paragraph 5)" if name != "Legacy Ensemble"
                         else "Algorithms provided by the commercial VarSeq software"),
        "source_locator": "Methods 'Splice prediction tools' and the list of options for the deep learning algorithms",
        "missing_metadata": {"version": {"reason": "unreported", "note": "Software or model release not printed"}},
    }, method_types=mt, links=[{"relation": "configuration_of", "target_id": SYSTEM[name]}])

# review correction 1: Riepe score rule for the deep learning rows
RIEPE_QUAL = "delta score for each variant's effect type; threshold optimised per gene and algorithm for maximum accuracy (upper bound)"
# review correction 5
RIEPE_UNION = ("The 213 variants are the union of the stored Riepe sets splicing-follow-up-20261009-data-riepe2021-abca4-di (81), "
               "-abca4-ncss (71) and -mybpc3-ncss (61).")
METHOD_NOTE = ("Parsed the pinned PMC13170886 article XML (table-wrap elements) with a stdlib reader; caption, header row and "
               "the four row labels asserted for each table; printed cell text kept exactly.")
links = []
for tid, cap, key, dname, dpop, ptext, qual, judged, loc in BENCH:
    tw = TABLES[tid]
    assert txt(tw.find("caption")).startswith(cap), (tid, txt(tw.find("caption")))
    rows = [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
    assert rows[0] == HEAD and [r[0] for r in rows[1:]] == ROWS, rows
    data = b.rid("data", key)
    b.entity("dataset", data, dname, f"{dname} as used by Fortier et al. 2026." + (" " + RIEPE_UNION if key == "riepe" else ""), [SRC], {
        "version": "As assembled by Fortier et al. 2026 (Supporting Information S1 to S5 Files)", "population": dpop,
        "split": "No split; whole set scored", "source_locator": loc.split(";")[0],
    })
    prot = b.rid("protocol", key)
    tnum = int(tid[-1])
    pname = f"Splice-altering variant classification, {dname} (Fortier et al. Table {tnum})"
    limits = ["Thresholds optimised on the same data for this benchmark, which may overestimate real-world performance (Discussion 'Study limitations')."] if key in ("riepe", "barbosa-deep-intronic") else []
    limits += ["Labels and variant sets are reused from earlier publications. CI-SpliceAI was trained on all human chromosomes, so no benchmark variant is held out from its training; "
               "ABCA4 lies on a test chromosome held out by both SpliceAI and OpenSpliceAI (Methods 'Technical overview of deep learning methods'; Discussion).",  # review correction 2
               "No uncertainty intervals are printed; significance is from two-proportion Z-tests on accuracy in the Results."]
    ci_dev = ["The variant set was assembled and published by the CI-SpliceAI developers (reference 9)."] if key == "ci-spliceai-benchmark" else []  # review correction 3
    b.entity("protocol", prot, pname, f"Binary splice-altering classification on the {dname}, scored by sensitivity, specificity, F1 and balanced accuracy.", [SRC], {
        "protocol": ptext, "version": f"Table {tnum}", "source_locator": loc, "limitations": limits + ci_dev,
    }, links=[{"relation": "uses_data", "target_id": data}])
    for row in rows[1:]:
        name = row[0]
        ev = b.rid("eval", key, CFG_DEF[name][0])
        rqual = RIEPE_QUAL if key == "riepe" and name != "Legacy Ensemble" else qual
        b.evaluation(ev, f"{name} on the {dname}", [SRC], CONFIG[name], prot, data,
                     "author_reported" if name == "Legacy Ensemble" else "independent_paper", {
                         "dataset_version": "As assembled by Fortier et al. 2026", "split": "Whole set", "population": dpop,
                         "inputs": "Variant with genomic sequence context (VCF)", "adaptation": rqual,
                         "metric_implementation": "Sensitivity, specificity, F1 = 2TP/(2TP+FP+FN), balanced accuracy = mean of sensitivity and specificity (Equations 1 to 4)",
                         "aggregation": "Whole dataset", "budget": None,
                     }, f"Table {tnum} row '{name}'")
        for (metric, col), cell in zip(METRICS, row[1:]):
            b.result(b.rid("result", key, CFG_DEF[name][0], metric), f"{name} {col} on the {dname} (Fortier et al. Table {tnum})",
                     SRC, [SRC], ev, cell, metric, "higher", "fraction", f"Table {tnum}, row '{name}', column '{col}'",
                     extraction_review(["deterministic-table-parse"], METHOD_NOTE, SHA, URL), qualifier=rqual)
    if judged:
        cid, _ = judgement(
            b, UC, UC_NAME, prot, pname, [SRC], [{"source_id": SRC, "locator": loc}], "proxy",
            f"Sensitivity, specificity, F1 and balanced accuracy of SpliceAI, CI-SpliceAI, OpenSpliceAI and a legacy N-of-4 vote on the {dname}",
            "Proxy: DNA-based splice predictors scored against experimentally established splicing outcomes, the sequence-classification kind of evidence the use case keeps separate from patient-RNA recovery; inputs are variants, not patient RNA-seq.",
            ["Inspect every linked evaluation's source locator before citing a result.",
             "Do not combine this mapping's evaluations with any other protocol's results; variant sets, labels and thresholds differ."],
            limits + ["Independent of the SpliceAI, CI-SpliceAI and OpenSpliceAI developers; the authors' employer supplies the Legacy Ensemble software, so those rows are author_reported.",
                      "Variant-level splicing effect, not pathogenicity or diagnostic yield; tissue context is not modelled."] + ci_dev,
            "balanced-accuracy", "fortier2026-spliceai-reimplementations", "SpliceAI and its open-source reimplementations on six splice benchmarks (Fortier et al. 2026)",
            dname, tnum,
            "Recorded from the 2026-10-11 use-case literature pass (data/omics/use-case-coverage-rna-splicing-20261011-fortier2026); pending independent review.")
        links.append({"use_case": UC, "relation": "assessed_by", "target_id": prot, "judgement_claim": cid})

finalize_review(b, {  # reviewed_evaluations: the four evaluations on each judged protocol
    "use-case-mapping-" + P + "-" + bench[2]: [P + "-eval-" + bench[2] + "-" + c[0] for c in CFG_DEF.values()] for bench in BENCH if bench[7]})
counts = b.write({"use-case-links.json": json.dumps({"note": "Proposed assessed_by links to add to the use_case record after the judgement claims are reviewed. Not applied by the extractor.", "links": links}, indent=1) + "\n"})
refresh_coverage(OUT)
print(json.dumps(counts))
