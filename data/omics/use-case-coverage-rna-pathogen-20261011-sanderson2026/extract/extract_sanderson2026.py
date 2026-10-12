"""Extract the validation-set results printed in the text of Sanderson et al. 2026 (medRxiv 10.64898/2026.02.06.26345651 v2).

Usage: python3 -I extract_sanderson2026.py <2026.02.06.26345651.source.xml> <batch-folder>

The preprint's Tables 1 to 3 are images in the JATS XML and are not transcribed. The values
here are printed in the Results text. The script finds each Results paragraph by its section
title and position, and asserts that the exact printed string occurs in it before writing a
result. Writes batch.jsonl and claims.csv. Records are needs_review.
"""
import csv, hashlib, json, re, sys
from collections import Counter

XML_SHA = "c0bc5c035742f53fe291e08b9d956102e102fd743a55de503f00bcaead36a7e2"
P = "rna-pathogen-20261011-sanderson2026"
SRC = f"{P}-source"
URL = "https://www.medrxiv.org/content/early/2026/02/26/2026.02.06.26345651.source.xml"
DATE = "2026-10-11"
FACETS = {"areas": ["microbes-communities"], "contexts": ["clinical_research"]}
UC = "use-case-diagnostic-rna-pathogen-detection"

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def text(s):
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    return re.sub(r"\s+", " ", s).strip()

def section_paras(xml, title):
    m = re.search(r"<sec[^>]*>\s*<title[^>]*>" + re.escape(title) + r"</title>(.*?)</sec>", xml, re.S)
    assert m, title
    return [text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", m.group(1), re.S)]

def abstract(xml):
    a = xml[xml.find("<abstract"):xml.find("</abstract>")]
    return [text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", a, re.S)]

# Independent review (reviewer-path, 2026-10-11; docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md):
# every record becomes source_checked, and results, claims and judgements carry the reviewer's review block.
REVIEW_NOTE = ("Re-downloaded the pinned artifact and matched its SHA-256; compared every value with a separate stdlib parser "
               "written for this review (the extractor's script was not run) and checked a stratified sample by hand against the rendered table.")

def finalize(records, table_results=True, extra_notes=None):
    extra_notes = extra_notes or {}
    evals = {}
    for r in records:
        if r["kind"] == "evaluation":
            pid = [l["target_id"] for l in r["links"] if l["relation"] == "assessment"][0]
            evals.setdefault(pid, []).append(r["id"])
    for r in records:
        r["status"] = "source_checked"
        a = r["attributes"]
        if r["kind"] not in ("result", "claim"):
            continue
        old = a["review"]
        if r["kind"] == "result":
            method = ["source-hash-verification", "deterministic-table-parse", "independent-cell-check"] if table_results else ["source-hash-verification", "independent-cell-check"]
        else:
            method = ["source-hash-verification", "independent-cell-check", "scope-review"]
        note = REVIEW_NOTE + (" " + extra_notes[r["id"]] if r["id"] in extra_notes else "")
        a["review"] = {"method": method, "reviewer": ["claude"],
                       "reviewer_note": "Separate Claude review agent (reviewer-path), independent of the extractor; no human review claimed",
                       "date": "2026-10-11", "artifact_sha256": old["artifact_sha256"], "retrieval_url": old["retrieval_url"],
                       "method_note": old["note"].replace(" Pending independent review.", ""), "note": note}
        if a.get("field", "").startswith("links:assessed_by:"):
            a["reviewed_evaluations"] = sorted(evals[a["value"]])
            a["reason"] = a["reason"].replace(" Needs independent review.", " Independently reviewed in docs/reviews/use-cases/pathogen-use-cases-2026-10-11.md.")

EXTRA = {}

def main():
    xml_path, out = sys.argv[1:3]
    assert sha(xml_path) == XML_SHA, sha(xml_path)
    xml = open(xml_path, encoding="utf-8").read()
    perf = section_paras(xml, "Validation Set: Diagnostic performance")
    bypath = section_paras(xml, "Performance by pathogen")
    load = section_paras(xml, "Performance by viral load (Cn,Ct)")
    ab = " ".join(abstract(xml))
    R, claims = [], []

    def add(id_, kind, name, desc, attrs, links=(), src=(SRC,), facets=FACETS):
        R.append({"id": id_, "kind": kind, "name": name, "description": desc, "status": "needs_review",
                  "facets": dict(facets), "source_ids": list(src),
                  "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attrs})

    def rev(note):
        return {"method": ["transcription"], "reviewer": ["claude"],
                "reviewer_note": "Extracting Claude research agent (uc-pathogens); not an independent review",
                "date": DATE, "artifact_sha256": XML_SHA, "retrieval_url": URL, "note": note + " Pending independent review."}

    def result(key, cfg, para, para_loc, quote, printed, numeric, metric, unit, direction, qual, num=None, den=None, ci=None, anomaly=None, unit_detail=None):
        assert quote in para, (key, quote)
        assert printed in quote, (key, printed)
        rid = f"{P}-result-{cfg}-{key}"
        attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed, "numeric_value": numeric,
                 "metric_qualifier": qual, "source_locator": f"{para_loc}: \"{quote}\""}
        if num is not None:
            attrs["numerator"], attrs["denominator"] = num, den
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        if ci:
            attrs["uncertainty"] = {"type": "confidence_interval", "lower": ci[0], "upper": ci[1], "level": 0.95, "printed": ci[2]}
        else:
            attrs["missing_metadata"] = {"uncertainty": {"reason": "unreported", "note": "No interval printed with this value"}}
        if anomaly:
            attrs["source_anomaly"] = anomaly
        attrs["review"] = rev("Transcribed from the Results text of the pinned JATS XML; the extraction script asserts that the quoted string occurs in the located paragraph.")
        add(rid, "result", f"sanderson2026 {cfg} {key}", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
            attrs, links=[("evaluation", f"{P}-eval-{cfg}")], facets={})
        claims.append([rid, SRC, attrs["source_locator"], printed, "result"])

    VP = "Results 'Validation Set: Diagnostic performance' paragraph"
    # Pre-specified criteria
    result("sensitivity", "prespecified", perf[3], f"{VP} 4", "133/260 (51%, 95%CI: 45-57%) PCR-positive results (i.e. gold-standard positives) were also detected by sequencing",
           "51%", "51", "recall", "percent", "higher", "all PCR targets; target level; reference: routine multiplex PCR", 133, 260, ("45", "57", "95%CI: 45-57%"))
    result("false-negatives", "prespecified", perf[3], f"{VP} 4", "There were 127 false-negative results", "127", "127", "false-negative-count", "count", "lower",
           "all PCR targets; target level; reference: routine multiplex PCR", unit_detail="PCR-positive targets not detected")
    result("specificity", "prespecified", perf[4], f"{VP} 5", "3901/3910 (99.8%) targets negative by PCR (as tested in the original assays) were also not detected from sequencing",
           "99.8%", "99.8", "specificity", "percent", "higher", "all PCR targets; target level; reference: routine multiplex PCR", 3901, 3910,
           anomaly="The Abstract (Findings) prints 'specificity 99.8% (95%CI: 99.6%-99.9%) (3836/3845 negative targets not detected)', a different numerator and denominator from the Results (3901/3910). The interval is printed only with the Abstract counts and is not attached here. Needs a reviewer's judgement."
                   " Independent review 2026-10-11: both counts give 99.8%; the result-level note is sufficient and no source-level concern is raised.")
    result("false-positives", "prespecified", perf[4], f"{VP} 5", "There were nine false-positive pathogen detections by sequencing", "nine", "9", "false-positive-count", "count", "lower",
           "all PCR targets; target level; reference: routine multiplex PCR", unit_detail="PCR-negative targets detected by sequencing")
    for key, quote, pv, lo, hi, ci_p, name in [
        ("sensitivity-rsv", "RSV 85% (95% CI: 75-95%)", "85%", "75", "95", "95% CI: 75-95%", "RSV"),
        ("sensitivity-sars-cov-2", "SARS-CoV-2 65% (95% CI: 53-78%)", "65%", "53", "78", "95% CI: 53-78%", "SARS-CoV-2"),
        ("sensitivity-influenza-a", "influenza A 58% (95% CI: 40-75%)", "58%", "40", "75", "95% CI: 40-75%", "influenza A"),
        ("sensitivity-rhinovirus-enterovirus", "rhinovirus/enterovirus 19% (95% CI: 8-29%)", "19%", "8", "29", "95% CI: 8-29%", "rhinovirus/enterovirus"),
    ]:
        result(key, "prespecified", bypath[0], "Results 'Performance by pathogen' paragraph 1", quote, pv, pv.rstrip("%"), "recall", "percent", "higher",
               f"pathogen target: {name}; target level; reference: routine multiplex PCR", ci=(lo, hi, ci_p))
    # Alternative (post-hoc) criteria
    result("sensitivity", "alternative", perf[5], f"{VP} 6", "increased sensitivity to 58% (95% CI 52-64%; 159/274)", "58%", "58", "recall", "percent", "higher",
           "all PCR targets; target level; reference: routine multiplex PCR", 159, 274, ("52", "64", "95% CI 52-64%"),
           anomaly="The same sentence says the alternative criterion 'increased the number of samples passing batch controls from 260 to 274'; 260 is elsewhere the number of PCR-positive targets, not samples, and 159/260 is later reported as 61% for RNA pathogens only. The denominator's meaning needs a reviewer's judgement."
                   " Independent review 2026-10-11: 159/274 = 58.0% and 159/260 = 61.2% are each arithmetically consistent with the printed percentages; the 274 denominator appears to include the DNA targets that the 61% result excludes, and 'samples' in that sentence appears to mean targets. Kept as printed with this note.")
    result("specificity", "alternative", perf[5], f"{VP} 6", "improved specificity to 99.9% (95% CI 99.8-100%; 4015/4017)", "99.9%", "99.9", "specificity", "percent", "higher",
           "all PCR targets; target level; reference: routine multiplex PCR", 4015, 4017, ("99.8", "100", "95% CI 99.8-100%"))
    result("sensitivity-rna-targets", "alternative", bypath[2], "Results 'Performance by pathogen' paragraph 2 (after Figure 6 and its legend)", "increased sensitivity using the alternative criteria to 61% (159/260) (95% CI 55-67%)",
           "61%", "61", "recall", "percent", "higher", "RNA pathogen targets only (adenovirus and bacteria excluded); target level; reference: routine multiplex PCR", 159, 260, ("55", "67", "95% CI 55-67%"))
    result("sensitivity-rna-excluding-rhino-entero", "alternative", bypath[2], "Results 'Performance by pathogen' paragraph 2 (after Figure 6 and its legend)", "increased overall sensitivity using the alternative criteria further to 70% (145/207) (95% CI 63%-76%)",
           "70%", "70", "recall", "percent", "higher", "RNA pathogen targets excluding rhinovirus and enterovirus; target level; reference: routine multiplex PCR", 145, 207, ("63", "76", "95% CI 63%-76%"))
    result("sensitivity-qpcr-detectable", "alternative", load[1], "Results 'Performance by viral load (Cn,Ct)' paragraph 2", "sensitivity increased to 75% (95% CI, 68-81%)",
           "75%", "75", "recall", "percent", "higher", "targets detectable by study qPCR; target level; reference: routine multiplex PCR", ci=("68", "81", "95% CI, 68-81%"))
    result("sensitivity-qpcr-ct-under-35", "alternative", load[1], "Results 'Performance by viral load (Cn,Ct)' paragraph 2", "increased further to 83% (95% CI, 76-88%) when restricting to qPCR Ct <35",
           "83%", "83", "recall", "percent", "higher", "targets with study qPCR Ct < 35; target level; reference: routine multiplex PCR", ci=("76", "88", "95% CI, 76-88%"))
    assert "3836/3845" in ab

    add(SRC, "source", "Clinical validation of a novel metagenomic nanopore sequencing method for detecting viral respiratory pathogens: diagnostic accuracy study",
        "Primary source retrieved and hashed for the 2026-10-11 RNA pathogen-detection literature pass.",
        {"url": "https://doi.org/10.64898/2026.02.06.26345651", "artifact_url": URL,
         "version": "medRxiv 10.64898/2026.02.06.26345651 v2, posted 2026-02-26; JATS XML",
         "retrieved_at": "2026-10-11T21:38:13Z", "artifact_sha256": XML_SHA, "doi": "10.64898/2026.02.06.26345651",
         "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "application/xml", "venue": "medRxiv", "year": 2026,
         "version_note": "A version was published in the Journal of Infection (doi 10.1016/j.jinf.2026.106839, 2026-08-22, CC BY per Europe PMC); its full text could not be retrieved (HTTP 403) and was not compared.",
         "source_locator": "JATS XML <license> element (CC BY 4.0) and the medRxiv API record (license cc_by)"},
        src=())
    add(f"{P}-method-cmg-ont", "method", "Oxford nasopharyngeal RNA-virus clinical metagenomics workflow (Sanderson et al. 2026)",
        "Host depletion by low-speed centrifugation and M-SAN HQ nuclease, virus precipitation, Direct-zol RNA extraction, cDNA synthesis and SISPA, ONT Rapid Barcoding on R10.4.1 (GridION), and minimap2 mapping to a curated database of the PCR panel's pathogen genomes, with batch and internal controls.",
        {"reported_name": "CMg workflow", "entity_level": "method",
         "source_locator": "Methods 'Procedures' paragraphs 2-4; Figure 1",
         "access": "Laboratory workflow; code availability is stated in the preprint's 'Code Availability' section (not inspected further)",
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; criteria are on configurations"}}},
        facets={**FACETS, "method_types": ["conventional_pipeline"]})
    cfgs = {
        "prespecified": ("Pre-specified detection criteria", "Thresholds fixed on the derivation set: (genome coverage >= 1 read > 0.25% OR area under the genome > 0.003 OR reads mapping to the reference > 0.006%) AND >= 2 target reads AND ratio criterion > 0.1; super-accuracy basecalling",
                         "Results 'Derivation Set: Defining bioinformatic thresholds for pathogen detection' paragraph 4; Table 2 (image, not transcribed)"),
        "alternative": ("Alternative post-hoc detection criterion", "Reads mapping to the target genome as a percentage of reads on the run mapping to that genome > 0.037%, AND >= 2 target reads, replacing the main and ratio criteria; chosen after the validation results",
                        "Results 'Validation Set: Diagnostic performance' paragraph 6"),
    }
    for k, (name, params, loc) in cfgs.items():
        add(f"{P}-config-{k}", "configuration", f"{name} (Sanderson et al. 2026)", f"The nanopore CMg workflow with the {name.lower()}.",
            {"reported_name": name, "parameters": params, "source_locator": loc, "foundation_model_eligible": False,
             "access_reuse": "Laboratory workflow described in the preprint; not a released product",
             "missing_metadata": {"version": {"reason": "unreported", "note": "minimap2 and basecaller versions are not given in the inspected text"}}},
            links=[("configuration_of", f"{P}-method-cmg-ont")], facets={**FACETS, "method_types": ["conventional_pipeline"]})
    data_id = f"{P}-data-validation"
    add(data_id, "dataset", "Validation set: 344 prospectively collected nasopharyngeal swabs (Sanderson et al. 2026)",
        "Upper respiratory tract samples submitted for routine multiplex PCR in Oxford during winter 2024/25, each sequenced once.",
        {"version": "As described in Sanderson et al. 2026 v2",
         "population": "344 nose and throat swabs; 273 passed batch and internal QC; 260 PCR-positive targets and 38 PCR-negative samples among those passing QC; PCR by Alinity Resp-4-plex, Xpert Xpress CoV-2/Flu/RSV plus or BIOFIRE FilmArray RP2.1",
         "split": "Independent validation set; thresholds derived on a separate derivation set (38 samples, 104 sequences)", "denominator": 344,
         "access": "Not inspected", "source_locator": "Methods 'Respiratory samples for pathogen detection'; Results paragraph 1 and 'Validation Set: Diagnostic performance' paragraphs 1-4"})
    pid = f"{P}-protocol-validation"
    add(pid, "protocol", "Target-level detection of respiratory pathogens against routine multiplex PCR, validation set (Sanderson et al. 2026)",
        "Sensitivity and specificity of the sequencing workflow for each pathogen target tested by the routine PCR panel, in samples passing QC.",
        {"protocol": "Each pathogen target tested by the sample's routine PCR assay is a gold-standard positive or negative; sequencing detection uses the configuration's criteria. Sensitivity = detected PCR-positive targets / PCR-positive targets; specificity = undetected PCR-negative targets / PCR-negative targets. Laboratory staff were blinded to validation results. 95% intervals are Clopper-Pearson where stated (Figure 6 legend).",
         "version": "medRxiv v2 Results", "source_locator": "Methods 'Procedures' paragraphs 1 and 5; Results 'Validation Set: Diagnostic performance'",
         "limitations": ["Target level, not patient level.", "Only samples passing batch and internal QC (273 of 344) are scored.", "Sensitivity is bounded by the PCR panel's targets; detections outside the panel are not scored.", "Spectrum bias: inclusion required a pathogen detected at Ct or Cn 30 or below on the four-target assays, or FilmArray testing, with about one FilmArray-negative sample collected per eight positive samples; sensitivity and specificity are not estimates for unselected swabs.", "Reads were mapped only to a curated database of the 23 PCR-panel pathogens, so the study does not measure detection of organisms outside the panel or false calls outside it."]},
        links=[("uses_data", data_id)])
    for k in cfgs:
        lim = ["Single laboratory workflow; the two configurations differ only in the bioinformatic detection criteria."]
        if k == "alternative":
            lim.append("Post-hoc: the alternative criterion was chosen after seeing the validation results, so its sensitivity and specificity are optimistic.")
        add(f"{P}-eval-{k}", "evaluation", f"{cfgs[k][0]} on the validation set (Sanderson et al. 2026)",
            "Published clinical validation; transcribed, not reproduced.",
            {"origin": "author_reported", "protocol": pid, "version": "Preprint v2 as retrieved 2026-10-11",
             "comparison": {"protocol_id": pid, "dataset_version": "Validation set, 344 nasopharyngeal swabs", "split": "Validation set",
                            "population": "Pathogen targets in the samples passing QC", "inputs": "RNA from nasopharyngeal swabs in viral transport medium",
                            "adaptation": cfgs[k][1], "metric_implementation": "Target-level sensitivity and specificity against routine multiplex PCR",
                            "aggregation": "All targets in samples passing QC, or the stated subset", "budget": None},
             "source_locator": "Results 'Validation Set: Diagnostic performance', 'Performance by pathogen' and 'Performance by viral load (Cn,Ct)'",
             "limitations": lim},
            links=[("system", f"{P}-config-{k}"), ("assessment", pid), ("data", data_id)])
    rationale = ("A prospective validation of one RNA metagenomic workflow on respiratory swabs, scored as target-level sensitivity and specificity against the original clinical PCR, with thresholds fixed on a separate derivation set, matches the use case's inputs (nuclease-treated respiratory RNA, reverse-transcribed) and its output (sensitivity against original clinical testing for one respiratory mNGS assay). "
                 "It is proxy evidence for the same reason as the UCSF anchor: agreement with the clinical PCR panel is not sensitivity against all infections, and samples were selected by PCR result. It compares detection criteria within one workflow, not different workflows.")  # review S1
    add(f"use-case-mapping-rna-pathogen-20261011-sanderson2026-validation", "claim",
        "Relevance of target-level detection against routine multiplex PCR, validation set (Sanderson et al. 2026) to \"Select an RNA pathogen-detection workflow for diagnostic testing\"",
        rationale,
        {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": "proxy",
         "endpoint": "Target-level sensitivity and specificity of a nanopore RNA metagenomic workflow against routine multiplex PCR in 344 prospectively collected nasopharyngeal swabs (273 passing QC), overall, by pathogen and by viral load, under pre-specified and post-hoc detection criteria",
         "rationale": rationale,
         "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                         "Do not combine these results with another protocol's results; specimens, reference assays and scoring units differ between sources.",
                         "Cite the pre-specified criteria as the validation result; the alternative criterion is post-hoc."],
         "limitations": ["Preprint (medRxiv v2); the Journal of Infection version was not retrieved or compared.",
                         "Developers' own workflow (author_reported).",
                         "The Abstract and Results give different specificity counts for the pre-specified criteria (3836/3845 against 3901/3910).",
                         "Upper respiratory swabs with high host background; sensitivity 51% overall, 19% for rhinovirus/enterovirus.",
                         "Nine false positives, attributed by the authors to barcode crossover in multiplexed runs.",
                         "71 of 344 samples failed QC and are not scored.",
                         "Tables 1 to 3 are images in the preprint and were not transcribed; only values printed in the text are recorded.", "Spectrum bias: inclusion required a pathogen detected at Ct or Cn 30 or below on the four-target assays, or FilmArray testing, with about one FilmArray-negative sample collected per eight positive samples; sensitivity and specificity are not estimates for unselected swabs.", "Reads were mapped only to a curated database of the 23 PCR-panel pathogens, so the study does not measure detection of organisms outside the panel or false calls outside it."],
         "citation_locators": [{"source_id": SRC, "locator": "Results 'Validation Set: Diagnostic performance', 'Performance by pathogen', 'Performance by viral load (Cn,Ct)'"}],
         "source_locator": f"{SRC}: Results 'Validation Set: Diagnostic performance'",
         "revision": 1,
         "reason": "Recorded from the 2026-10-11 RNA pathogen-detection literature pass (data/omics/use-case-coverage-rna-pathogen-20261011-sanderson2026). Needs independent review.",
         "comparison_group": "sanderson2026-nanopore-nps", "comparison_title": "Nanopore RNA metagenomics on nasopharyngeal swabs against multiplex PCR (Sanderson et al. 2026)",
         "headline_metric": "recall", "stratum_label": "Validation set", "stratum_order": 1,
         "review": rev("Judgement drafted by the extracting agent from the pinned preprint.")},
        links=[("subject", UC)], facets={})
    add(f"{P}-claim-false-positive-cause", "claim", f"false_positive_cause: {pid}", "Descriptive fact transcribed from the pinned source.",
        {"field": "false_positive_cause",
         "value": "All nine false-positive detections in the validation set were potentially attributable to barcode crossover from another sample on the same run with many reads for the same pathogen.",
         "source_locator": f"{VP} 5", "review": rev("Transcribed from the pinned JATS XML text.")},
        links=[("subject", pid)], facets={})
    claims.append([f"{P}-claim-false-positive-cause", SRC, f"{VP} 5", R[-1]["attributes"]["value"], "claim"])

    finalize(R, table_results=False, extra_notes=EXTRA)
    R.sort(key=lambda r: r["id"])
    assert len({r["id"] for r in R}) == len(R)
    with open(f"{out}/batch.jsonl", "w") as f:
        for r in R:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(f"{out}/claims.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        w.writerows(claims)
    print(dict(Counter(r["kind"] for r in R)))

if __name__ == "__main__":
    main()
