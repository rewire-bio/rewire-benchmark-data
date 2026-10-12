"""Extract Hwang et al. 2026 (Genes 17(1):105) Table 4 into batch records.

Usage: python3 -I extract_hwang2026.py <PMC12841491 fullTextXML> <batch folder>
Parses Table 4 from the pinned Europe PMC article XML, asserts the caption, the two header rows and the six row
labels, and writes needs_review records. Tables 1 to 3 describe the reference set, call counts and features of
true and false negatives; they hold no per-tool accuracy and are not extracted.
"""
import json, os, re, sys
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, finalize_review, judgement, refresh_coverage, sha256

XML, OUT = sys.argv[1], sys.argv[2]
SHA = "ff82a186d0adcf319b603a1100427ec0f6ed95becf040b512d0aef5e515bdc5d"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12841491/fullTextXML"
assert sha256(XML) == SHA

P = "cnv-20261011-hwang2026"
b = Batch(OUT, P, areas=["dna-genomes"])
SRC = P + "-source-article"
UC = "use-case-cnv-detection-characterisation"
UC_NAME = "Select a copy-number variant detection and characterisation workflow"

b.source(SRC, "Improving CNV Detection Performance Except for Software-Specific Problematic Regions (Hwang et al., Genes 2026)", {
    "url": "https://doi.org/10.3390/genes17010105",
    "artifact_url": URL,
    "version": "Genes 17(1):105, published 2026-01-19; PMC12841491 full-text XML",
    "retrieved_at": "2026-10-11T21:36:59Z",
    "artifact_sha256": SHA,
    "doi": "10.3390/genes17010105",
    "publication_status": "peer_reviewed",
    "licence": "CC-BY-4.0",
    "media_type": "application/xml",
    "limitations": [
        "Abstract gives ExomeDepth gains of 14.4% in sensitivity and 7.9% in PPV after filtering; Table 4 gives 0.758 to 0.903 (14.5 points) and 0.025 to 0.102 (7.7 points).",
        "Results 3.3 says ExomeDepth PPV 'increased five-fold'; Table 4 gives 0.025 to 0.102, about four-fold.",
        "Supplementary files (one zip) were not retrieved.",
        # review correction 1
        "The Abstract says all tools improved after filtration; Table 4 gives cn.MOPS sensitivity falling from 0.170 to 0.162.",
    ],
})

root = ET.parse(XML).getroot()
def txt(e): return " ".join("".join(e.itertext()).split())
tw = [t for t in root.iter("table-wrap") if t.get("id") == "genes-17-00105-t004"][0]
assert txt(tw.find("label")) == "Table 4" and txt(tw.find("caption")) == "Performance of the four CNV detection programs."
rows = [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
TOOLS = ["ExomeDepth", "CNVkit", "CoNIFER", "cn.MOPS"]
assert rows[0] == [""] + TOOLS, rows[0]
assert rows[1] == [""] + ["Pre-filter", "Post-filter"] * 4, rows[1]
LABELS = ["Reference Truth set", "TP", "FP", "FN", "Sensitivity", "PPV"]
assert [r[0] for r in rows[2:]] == LABELS and all(len(r) == 9 for r in rows[2:])

METHOD = {"ExomeDepth": "rare-reanalysis-20261009-method-exomedepth", "CoNIFER": "rare-reanalysis-20261009-method-conifer",
          "cn.MOPS": "cnv-20261009-method-cn-mops"}
METHOD["CNVkit"] = b.rid("method", "cnvkit")
b.entity("method", METHOD["CNVkit"], "CNVkit", "Read-depth copy-number caller for targeted and exome sequencing.", [SRC], {
    "reported_name": "CNVkit", "entity_level": "method", "source_locator": "Methods 2.3",
    "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the version used is on the configuration"}},
}, method_types=["conventional_pipeline"])
VERSION = {"ExomeDepth": ("v1.1.15", "default parameters"), "CNVkit": ("v0.9.7", "default parameters"),
           "CoNIFER": ("v0.2.2", "singular value decomposition parameter 8"), "cn.MOPS": ("v1.14.1", "default parameters")}
FILTER = ("CNV calls overlapping the tool's problematic regions removed (regions where the tool called CNVs in more than 10% "
          "of the 180-sample WES cohort; Methods 2.5)")
CFG = {}
for tool in TOOLS:
    for stage in ("pre-filter", "post-filter"):
        key = re.sub(r"[^a-z0-9]+", "-", tool.lower()).strip("-") + "-" + stage
        CFG[(tool, stage)] = b.rid("config", key)
        version, params = VERSION[tool]
        b.entity("configuration", CFG[(tool, stage)], f"{tool} {version}, {stage} (Hwang et al. 2026)",
                 f"{tool} on clinical exomes" + (" with the authors' problematic-region filter." if stage == "post-filter" else " with the stated parameters."),
                 [SRC], {"reported_name": f"{tool} ({stage})", "foundation_model_eligible": False, "version": version,
                         "parameters": params + ("; " + FILTER if stage == "post-filter" else ""),
                         "access_reuse": "Open-source tool", "source_locator": "Methods 2.3 and 2.5; Table 4 column header"},
                 method_types=["conventional_pipeline"], links=[{"relation": "configuration_of", "target_id": METHOD[tool]}])

DATA = b.rid("data", "korea-wes-cma-39")
b.entity("dataset", DATA, "Korea University clinical exomes with CMA reference CNVs (Hwang et al. 2026)",
         "Clinical WES of 180 unrelated patients; 44 also had chromosomal microarray, of whom 39 contributed 98 high-quality reference CNVs spanning 2,788 exons.",
         [SRC], {"version": "As published (raw data not shared in the article)",
                 "assay": "Agilent SureSelect Human All Exon v6, Illumina NovaSeq 6000 2 x 150 bp, mean on-target depth 110x; BWA-MEM v0.7.17 to GRCh37; CMA on CytoScan Dx and 750K arrays analysed with ChAS",
                 "population": "39 CMA-positive individuals; 98 reference CNVs (39 deletions, 59 duplications; 5.03 kb to 6.91 Mb) covering 2,058 deleted and 730 duplicated exons; the other 141 exomes were used only to define problematic regions",
                 "split": "No split", "source_locator": "Methods 2.1 and 2.2; Table 1; Results 3.1"})

COMMON = ["Exome input, not the whole-genome input this use case names.",
          "Exon-level scoring against CMA-derived truth: CMA misses small CNVs and only CNVs overlapping exome baits were kept, so precision counts any exon call outside that truth as false.",
          "39 individuals from one centre; no uncertainty intervals are printed."]
PROTS = {
    "pre-filter": dict(name="Exon-level CNV detection in clinical exomes against CMA truth, default calls (Hwang et al. Table 4, pre-filter)",
        protocol="Call CNVs with each tool on the 39 CMA-positive exomes; count CMA CNV exons detected (TP), missed (FN) and called exons outside the reference (FP); report sensitivity and PPV.",
        limits=[], origin="independent_paper"),
    "post-filter": dict(name="Exon-level CNV detection in clinical exomes against CMA truth, after removing tool-specific problematic regions (Hwang et al. Table 4, post-filter)",
        protocol="As pre-filter, after removing calls in each tool's problematic regions; reference exons in those regions are also removed, so the reference count differs by tool (2,124 to 2,723 of 2,788).",
        limits=["The filter is the authors' method and is defined on the same 180-sample cohort, including the 39 evaluated exomes.",
                "The reference truth set shrinks after filtering (Table 4 row 'Reference Truth set'), so post-filter sensitivity is on fewer exons."],
        origin="author_reported"),
}
PID = {}
for stage, p in PROTS.items():
    PID[stage] = b.rid("protocol", stage)
    b.entity("protocol", PID[stage], p["name"], p["protocol"], [SRC], {
        "protocol": p["protocol"], "version": "Table 4", "source_locator": "Table 4; Methods 2.2, 2.4 and 2.5; Results 3.3",
        "limitations": p["limits"] + COMMON}, links=[{"relation": "uses_data", "target_id": DATA}])

MET = {"Reference Truth set": ("count", "unknown", "count", "reference CMA CNV exons in the evaluated set"),
       "TP": ("true-positive-count", "higher", "count", None), "FP": ("false-positive-count", "lower", "count", None),
       "FN": ("false-negative-count", "lower", "count", None), "Sensitivity": ("recall", "higher", "fraction", None),
       "PPV": ("precision", "higher", "fraction", None)}
METHOD_NOTE = "Parsed the pinned PMC12841491 article XML (table-wrap genes-17-00105-t004) with a stdlib reader; caption, both header rows and six row labels asserted; printed cell text kept exactly, thousands separators removed only in numeric_value."
for ti, tool in enumerate(TOOLS):
    for si, stage in enumerate(("pre-filter", "post-filter")):
        col = 1 + 2 * ti + si
        ev = b.rid("eval", stage, CFG[(tool, stage)].split("-config-")[1].replace("-" + stage, ""))
        b.evaluation(ev, f"{tool} ({stage}) on 39 clinical exomes against CMA truth", [SRC], CFG[(tool, stage)], PID[stage], DATA, PROTS[stage]["origin"], {
            "dataset_version": "Korea University clinical WES and CMA, January 2021 to June 2023 (as published)", "split": "No split",
            "population": "39 CMA-positive individuals; 98 reference CNVs, 2,788 reference exons before filtering",
            "inputs": "Clinical exome alignments (GRCh37)", "adaptation": None,
            "metric_implementation": "Exon-level sensitivity TP/(TP+FN) and PPV TP/(TP+FP) (Methods 2.4)", "aggregation": "Pooled over 39 individuals", "budget": None,
        }, f"Table 4 column '{tool}' / '{stage.capitalize()}'", missing={"comparison.adaptation": {"reason": "inapplicable", "note": "No training on the evaluation data"}})
        for r in rows[2:]:
            cell = r[col]
            metric, direction, unit, qual = MET[r[0]]
            numeric = cell.replace(",", "") if re.fullmatch(r"\d{1,3}(,\d{3})+|\d+(\.\d+)?", cell) else None
            b.result(b.rid("result", stage, tool, r[0]), f"{tool} {stage} {r[0]} (Hwang et al. Table 4)", SRC, [SRC], ev, cell, metric, direction, unit,
                     f"Table 4, row '{r[0]}', column '{tool}' / '{stage.capitalize()}'", extraction_review(["deterministic-table-parse"], METHOD_NOTE, SHA, URL),
                     qualifier=("exon level; " + qual) if qual else "exon level", unit_detail="exons" if unit == "count" else None, numeric=numeric)

links = []
for order, stage in enumerate(PROTS, start=1):
    cid, _ = judgement(
        b, UC, UC_NAME, PID[stage], PROTS[stage]["name"], [SRC], [{"source_id": SRC, "locator": "Table 4; Methods 2.2 to 2.5; Results 3.3"}], "proxy",
        "Exon-level TP, FP and FN counts with sensitivity and PPV of ExomeDepth, CNVkit, CoNIFER and cn.MOPS against CMA CNVs in clinical exomes" + (", after the problematic-region filter" if stage == "post-filter" else ""),
        "Proxy: germline CNV detection accuracy against an orthogonal array truth set, but from exome rather than whole-genome data and scored per exon; it covers duplications as well as deletions.",
        ["Inspect every linked evaluation's source locator before citing a result.",
         "Do not combine this mapping's evaluations with any other protocol's results; inputs, truth and matching rules differ."],
        PROTS[stage]["limits"] + COMMON,
        "recall", "hwang2026-wes-cnv", "Exome CNV callers against CMA truth, before and after removing problematic regions (Hwang et al. 2026)",
        "Default calls" if stage == "pre-filter" else "After problematic-region filter", order,
        "Recorded from the 2026-10-11 use-case literature pass (data/omics/use-case-coverage-cnv-20261011-hwang2026); pending independent review.")
    links.append({"use_case": UC, "relation": "assessed_by", "target_id": PID[stage], "judgement_claim": cid})

finalize_review(b, {  # reviewed_evaluations as listed by reviewer-scnv
    "use-case-mapping-cnv-20261011-hwang2026-pre-filter": [P + "-eval-pre-filter-" + t for t in ("cn-mops", "cnvkit", "conifer", "exomedepth")],
    "use-case-mapping-cnv-20261011-hwang2026-post-filter": [P + "-eval-post-filter-" + t for t in ("cn-mops", "cnvkit", "conifer", "exomedepth")],
})
counts = b.write({"use-case-links.json": json.dumps({"note": "Proposed assessed_by links to add to the use_case record after the judgement claims are reviewed. Not applied by the extractor.", "links": links}, indent=1) + "\n"})
refresh_coverage(OUT)
print(json.dumps(counts))
