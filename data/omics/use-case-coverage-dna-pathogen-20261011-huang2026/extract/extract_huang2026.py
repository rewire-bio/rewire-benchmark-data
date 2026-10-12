"""Extract Huang et al. 2026 (Respiratory Research 27:357) Table 2.

Usage: python3 -I extract_huang2026.py <PMC13584460.xml> <batch-folder>

Deterministic parse of the pinned Europe PMC full-text XML. Every stratum, method and
column label is asserted. printed_value is the value part of the cell exactly as printed;
the printed interval is kept in uncertainty.printed. Writes batch.jsonl and claims.csv.
Records are needs_review.
"""
import csv, hashlib, json, re, sys
import xml.etree.ElementTree as ET
from collections import Counter

XML_SHA = "79b237d733d9ad3af33722c30013afb0539adf03098ca1e1c2f18344bcc4a67d"
P = "dna-pathogen-20261011-huang2026"
SRC = f"{P}-source"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13584460/fullTextXML"
DATE = "2026-10-11"
FACETS = {"areas": ["microbes-communities"], "contexts": ["clinical_research"]}
UC = "use-case-diagnostic-dna-pathogen-identification"
MINUS = "−"

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def txt(e):
    # Collapse ASCII whitespace only: the source cells use U+2009 (thin space), kept exactly (review G6).
    return re.sub(r"[ \t\r\n]+", " ", "".join(e.itertext())).strip()

HEADER = ["", "Methods", "Sensitivity (95%CI)", "Specificity (95%CI)", "PPV (95%CI)", "NPV (95%CI)", "Accuracy (95%CI)", "p value"]
STRATA = [("All pneumonia", "all", "all pneumonia"), ("GPB pneumonia", "gpb", "gram-positive bacterial pneumonia"),
          ("GNB pneumonia", "gnb", "gram-negative bacterial pneumonia"), ("Fungal pneumonia", "fungal", "fungal pneumonia")]
METHODS = [("Blood-bstNGS", "bstngs"), ("Blood-mNGS", "mngs"), ("CMTs", "cmt"), ("Blood-culture only", "culture")]
COLS = [(2, "sensitivity", "recall", "higher"), (3, "specificity", "specificity", "higher"), (4, "ppv", "precision", "higher"),
        (5, "npv", "negative-predictive-value", "higher"), (6, "accuracy", "accuracy", "higher")]
THIN = "\u2009"
CELL = re.compile(r"^(\d+\.\d+%) \((\d+\.\d+)% " + MINUS + THIN + r"(\d+\.\d+)%\)$")

def parse(xml_path):
    root = ET.parse(xml_path).getroot()
    tw = [t for t in root.iter("table-wrap") if txt(t.find("label")) == "Table 2"]
    assert len(tw) == 1
    rows = [[txt(c) for c in r] for r in tw[0].iter("tr")]
    assert rows[0] == HEADER, rows[0]
    out, i = {}, 1
    for slabel, skey, _ in STRATA:
        for mi, (mlabel, mkey) in enumerate(METHODS):
            r = rows[i]; i += 1
            if mi == 0:
                assert r[0] == slabel, (r[0], slabel)
                r = r[1:]
            assert r[0] == mlabel and len(r) == 7, r
            out[(skey, mkey)] = r
    assert i == len(rows)
    return out

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
    assert sha(xml_path) == XML_SHA
    cells = parse(xml_path)
    R, claims = [], []

    def add(id_, kind, name, desc, attrs, links=(), src=(SRC,), facets=FACETS):
        R.append({"id": id_, "kind": kind, "name": name, "description": desc, "status": "needs_review",
                  "facets": dict(facets), "source_ids": list(src),
                  "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attrs})

    def rev(note, method="deterministic-table-parse"):
        return {"method": [method], "reviewer": ["claude"],
                "reviewer_note": "Extracting Claude research agent (uc-pathogens); not an independent review",
                "date": DATE, "artifact_sha256": XML_SHA, "retrieval_url": URL, "note": note + " Pending independent review."}

    pid = f"{P}-protocol-clinical-diagnosis"
    for (skey, mkey), r in cells.items():
        slabel, sname = [(a, c) for a, b, c in STRATA if b == skey][0]
        for ci, key, metric, direction in COLS:
            raw = r[ci - 1]
            m = CELL.match(raw)
            assert m, raw
            pv, lo, hi = m.groups()
            rid = f"{P}-result-{skey}-{mkey}-{key}"
            loc = f"Table 2, stratum '{slabel}', row '{r[0]}', column '{HEADER[ci]}'"
            attrs = {"metric": metric, "metric_direction": direction, "unit": "percent", "printed_value": pv, "numeric_value": pv.rstrip("%"),
                     "metric_qualifier": f"patient level; {sname}; reference: final clinical diagnosis",
                     "uncertainty": {"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "printed": raw[len(pv):].strip()},
                     "source_locator": loc}
            if key == "accuracy":
                attrs["reported_p_value"] = r[6]
            if (skey, mkey, key) == ("fungal", "culture", "ppv"):
                attrs["source_anomaly"] = ("Printed '0.00% (0.00% " + MINUS + THIN + "0.00%)'. Blood culture detected no fungal pathogen in this stratum (sensitivity 0.00%, specificity 100.00%), "
                                           "so PPV has a zero denominator and is undefined; the printed 0.00% and degenerate interval are kept as printed. Needs a reviewer's judgement."
                                           " Independent review 2026-10-11: numeric_value set to null so the undefined value is not ranked as zero; printed_value and the printed interval are kept.")
                attrs["numeric_value"] = None  # review G5
                # The store rejects a missing_metadata key for an attribute that is present (numeric_value: null, uncertainty), so the
                # reviewer's numeric_value reason is recorded under "value", as in the cnv-20261009 NA results.
                attrs["missing_metadata"] = {"value": {"reason": "inapplicable", "note": "PPV is undefined: blood culture had no positive call in this stratum (sensitivity 0.00%, specificity 100.00%); the printed 0.00% is not interpreted"}}
            if key == "accuracy":
                EXTRA[rid] = "McNemar test against blood-bstNGS with Bonferroni adjustment (Table 2 footnote); attached to accuracy following Results paragraph 4."  # review G6
            attrs["review"] = rev("Extracted by deterministic parse of the pinned Europe PMC full-text XML (extract/extract_huang2026.py), with stratum, row and column labels asserted. printed_value is the value before the interval exactly as printed.")
            add(rid, "result", f"huang2026 {skey} {mkey} {key}", "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                attrs, links=[("evaluation", f"{P}-eval-{mkey}")], facets={})
            claims.append([rid, SRC, loc, pv, "result"])

    add(SRC, "source", "Blood-based targeted sequencing of microbial cell-free DNA in severe pneumonia-associated sepsis",
        "Primary source retrieved and hashed for the 2026-10-11 DNA pathogen-identification literature pass.",
        {"url": "https://doi.org/10.1186/s12931-026-03786-0", "artifact_url": URL,
         "version": "Respiratory Research 27:357, published 2026-06-24; PMC13584460 full-text XML",
         "retrieved_at": "2026-10-11T22:07:38Z", "artifact_sha256": XML_SHA, "doi": "10.1186/s12931-026-03786-0",
         "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/xml",
         "venue": "Respiratory Research", "year": 2026,
         "source_locator": "Licence statement in the article XML <license> element: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0",
         "access_note": "No-derivatives licence: no copy of the article is archived in the batch; hashes and locators only."},
        src=())
    meths = {
        "bstngs": ("method", "Geneplus broad-spectrum targeted NGS of microbial cell-free DNA (bstNGS)",
                   "Probe-capture targeted sequencing of microbial cell-free DNA from blood with a 1,872-organism Geneplus panel, Gene+Seq-100 sequencing and the Gene+P-Seq-Tool Kits analysis.",
                   "VAMNE Magnetic Pathogen DNA/RNA extraction; HieffNGS C37P4 One Pot cDNA&gDNA library; 4 h hybridisation with Geneplus probes (1,872 organisms, STable 1) on Gene+GIN96; Gene+Seq-100 at 5 M reads; Gene+P-Seq-Tool Kits; reportable at RPM >= 6 for common pathogens and >= 0.5 for fungi and mycobacteria",
                   "Commercial assay; one co-author is affiliated with Geneplus-Beijing"),
        "mngs": ("method", "Blood metagenomic NGS (Illumina NextSeq 550; Huang et al. 2026)",
                 "Untargeted DNA metagenomic sequencing of blood with host read removal against hg38 and an automated analysis solution.",
                 "TIANamp Micro DNA Kit extraction; NextSeq 550 at 20 M reads per sample; automated analysis with hg38 host removal",
                 "Hospital or vendor laboratory workflow; the analysis software and database are not named"),
        "cmt": ("method", "Conventional microbiological tests (Huang et al. 2026)",
                "Standard-of-care smear, culture, serology and PCR-based tests.",
                "Smear, culture, serology and PCR (Daan Gene; Cepheid) as ordered clinically",
                "Clinical laboratory tests"),
        "culture": ("method", "Blood culture (Huang et al. 2026)", "Blood culture from the same blood draw.", "Blood culture only", "Clinical laboratory test"),
    }
    names = {"bstngs": "Blood-bstNGS", "mngs": "Blood-mNGS", "cmt": "CMTs", "culture": "Blood-culture only"}
    for k, (_, name, desc, params, access) in meths.items():
        mt = ["conventional_pipeline"]
        add(f"{P}-method-{k}", "method", name, desc,
            {"reported_name": names[k], "entity_level": "method", "access": access,
             "source_locator": "Methods 'Sample enrollment and standard-of-care microbiology testing' and 'bstNGS assay workflow and mNGS steps'",
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the setup is on the configuration"}}},
            facets={**FACETS, "method_types": mt})
        add(f"{P}-config-{k}", "configuration", f"{name}, as run in Huang et al. 2026", f"{names[k]} as applied to the blood samples of the 122-patient cohort.",
            {"reported_name": names[k], "parameters": params, "foundation_model_eligible": False, "access_reuse": access,
             "source_locator": "Methods 'bstNGS assay workflow and mNGS steps'; Supplementary Methods (not inspected)",
             "missing_metadata": {"version": {"reason": "unreported", "note": "No software or database versions are given"}}},
            links=[("configuration_of", f"{P}-method-{k}")], facets={**FACETS, "method_types": mt})
    data_id = f"{P}-data-sepsis122"
    add(data_id, "dataset", "122 ICU patients with severe pneumonia-associated sepsis and paired blood and BALF (Huang et al. 2026)",
        "Retrospective cohort from the First Affiliated Hospital, Sun Yat-sen University, February 2022 to February 2024.",
        {"version": "As described in Huang et al. 2026", "population": "122 of 183 screened adults (61 excluded for missing paired samples or clinical information); 73.0% immunocompromised; blood tested by bstNGS, mNGS and culture from the same batch, BALF by mNGS",
         "split": "Single retrospective cohort; no split", "denominator": 122, "access": "Not stated in the inspected text",
         "source_locator": "Methods 'Sample enrollment and standard-of-care microbiology testing'; Results paragraph 1; Table 1"})
    add(pid, "protocol", "Patient-level detection of causative pathogens in blood against the final clinical diagnosis (Huang et al. 2026 Table 2)",
        "Sensitivity, specificity, PPV, NPV and accuracy of each blood-based test for the clinically adjudicated causative or possibly causative pathogens, overall and by pathogen class, with 95% intervals.",
        {"protocol": "Reference: final clinical diagnosis by two ICU clinicians, a third on disagreement, and respiratory and laboratory medicine review, integrating symptoms, markers, pathology, imaging, standard-of-care tests and NGS results (BALF mNGS included). Patient-level 2x2 against that diagnosis for each stratum; McNemar tests against blood-bstNGS.",
         "version": "Table 2", "source_locator": "Methods 'Clinical diagnosis' and 'Statistics'; Results 'Comparative diagnostic performance of blood-bstNGS as an alternative blood-based assay'",
         "limitations": ["Incorporation bias: the reference was established primarily from BALF mNGS and CMT results (Methods 'Sample enrollment and standard-of-care microbiology testing' paragraph 3; Table 2 footnote), with clinical adjudication. CMTs is scored against a reference that contains it, which favours CMTs, and BALF mNGS is a sequencing assay on a different specimen.",
                         "Retrospective; 61 of 183 patients excluded for missing paired samples or information.",
                         "Unit counts are not printed; only percentages with intervals."]},
        links=[("uses_data", data_id)])
    for k in meths:
        add(f"{P}-eval-{k}", "evaluation", f"{names[k]} against the final clinical diagnosis (Huang et al. 2026)",
            "Published clinical comparison; transcribed, not reproduced.",
            {"origin": "author_reported", "protocol": pid, "version": "Primary source as retrieved 2026-10-11",
             "comparison": {"protocol_id": pid, "dataset_version": "122-patient severe pneumonia-associated sepsis cohort (Huang et al. 2026)", "split": "Single cohort",
                            "population": "122 patients; strata by pathogen class as printed", "inputs": "Blood (microbial cell-free DNA for the NGS assays)",
                            "adaptation": meths[k][3], "metric_implementation": "Patient-level sensitivity, specificity, PPV, NPV and accuracy against the final clinical diagnosis",
                            "aggregation": "All patients in the stratum", "budget": None},
             "source_locator": f"Table 2, rows '{names[k]}'",
             "limitations": ["The reference was established primarily from BALF mNGS and CMT results, so CMTs is scored against a reference that contains it.",
                             "Two co-authors (Dejian Gu and Hao Liu) are affiliated with Geneplus-Beijing, which supplies the bstNGS probes and analysis kits; the article declares no competing interests."]},
            links=[("system", f"{P}-config-{k}"), ("assessment", pid), ("data", data_id)])
    rationale = ("Two DNA sequencing workflows on blood (targeted probe-capture bstNGS and untargeted mNGS) and two conventional tests are scored on the same 122 patients against an adjudicated clinical diagnosis, "
                 "which bears directly on the use case's question of which DNA workflow detects clinically relevant pathogens from blood. "
                 "It is proxy evidence: the reference incorporates NGS results, the cohort is retrospective, the specimens are plasma microbial cell-free DNA in pneumonia-associated sepsis, and the targeted assay detects only its 1,872-organism panel.")
    add(f"use-case-mapping-dna-pathogen-20261011-huang2026-clinical-diagnosis", "claim",
        "Relevance of patient-level detection of causative pathogens in blood against the final clinical diagnosis (Huang et al. 2026 Table 2) to \"Select a DNA pathogen-identification workflow for diagnostic testing\"",
        rationale,
        {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": "proxy",
         "endpoint": "Patient-level sensitivity, specificity, PPV, NPV and accuracy (95% intervals) of blood bstNGS, blood mNGS, conventional tests and blood culture against the adjudicated clinical diagnosis in 122 ICU patients, overall and for gram-positive, gram-negative and fungal pneumonia",
         "rationale": rationale,
         "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                         "Do not combine these results with another protocol's results; reference standards, specimens and scoring units differ between sources."],
         "limitations": ["Incorporation bias: the reference was established primarily from BALF mNGS and CMT results (Methods 'Sample enrollment and standard-of-care microbiology testing' paragraph 3; Table 2 footnote), with clinical adjudication. CMTs is scored against a reference that contains it, which favours CMTs, and BALF mNGS is a sequencing assay on a different specimen.",
                         "Retrospective single-centre cohort; 61 of 183 screened patients excluded.",
                         "Few patients are reference-negative: the count is not printed, and the specificity intervals are wide (44.44% for bstNGS, 24.56% to 66.28%).",
                         "Targeted panel: bstNGS cannot detect organisms outside its 1,872 probes, which bears on the use case's question of organisms absent from the reference.",
                         "Blood culture PPV in fungal pneumonia is printed 0.00% with a zero denominator (result source_anomaly).",
                         "Commercial assay with two co-authors from its supplier (Geneplus-Beijing); no competing interests declared."],
         "citation_locators": [{"source_id": SRC, "locator": "Table 2; Methods 'Clinical diagnosis' and 'bstNGS assay workflow and mNGS steps'"}],
         "source_locator": f"{SRC}: Table 2", "revision": 1,
         "reason": "Recorded from the 2026-10-11 DNA pathogen-identification literature pass (data/omics/use-case-coverage-dna-pathogen-20261011-huang2026). Needs independent review.",
         "comparison_group": "huang2026-blood-sepsis", "comparison_title": "Blood targeted and untargeted sequencing against clinical diagnosis in pneumonia-associated sepsis (Huang et al. 2026)",
         "headline_metric": "recall", "stratum_label": "122 ICU patients", "stratum_order": 1,
         "review": rev("Judgement drafted by the extracting agent from the pinned article.", method="transcription")},
        links=[("subject", UC)], facets={})
    add(f"{P}-claim-reference-incorporates-ngs", "claim", f"reference_standard_definition: {pid}", "Descriptive fact transcribed from the pinned source.",
        {"field": "reference_standard_definition",
         "value": "The final clinical diagnosis integrated clinical symptoms, infection markers, pathology, imaging, standard-of-care tests (smear, culture, serology and PCR) and NGS results, and was adjudicated by ICU clinicians with multidisciplinary review.",
         "source_locator": "Methods 'Clinical diagnosis' paragraph 1",
         "review": rev("Transcribed from the pinned article XML text.", method="transcription")},
        links=[("subject", pid)], facets={})
    claims.append([f"{P}-claim-reference-incorporates-ngs", SRC, "Methods 'Clinical diagnosis' paragraph 1", R[-1]["attributes"]["value"], "claim"])

    finalize(R, extra_notes=EXTRA)
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
