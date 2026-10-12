"""Extract Wolf et al. 2026 (Lancet Microbe 7:101312) Tables 2 and 3.

Usage: python3 -I extract_wolf2026.py <PMC13154368.xml> <batch-folder>

Deterministic parse of the pinned Europe PMC full-text XML. Every row and column label is
asserted. printed_value is the cell text exactly, including the U+00B7 decimal point;
numeric_value converts it to a decimal string. Writes batch.jsonl and claims.csv.
Records are needs_review.
"""
import csv, hashlib, json, re, sys
import xml.etree.ElementTree as ET
from collections import Counter

XML_SHA = "0f6905d0a0c9ace686bcc61970c711558ccf530b5c31f882607a305f8b5ca689"
P = "dna-pathogen-20261011-wolf2026"
SRC = f"{P}-source"
URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13154368/fullTextXML"
DATE = "2026-10-11"
FACETS = {"areas": ["microbes-communities"], "contexts": ["clinical_research"]}
UC = "use-case-diagnostic-dna-pathogen-identification"
DOT = "·"

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def txt(e):
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()

def table(root, label):
    tw = [t for t in root.iter("table-wrap") if txt(t.find("label")) == label]
    assert len(tw) == 1, label
    return [[txt(c) for c in r] for r in tw[0].iter("tr")]

PCT = re.compile(r"^(\d+" + DOT + r"\d)% \((\d+" + DOT + r"\d)–(\d+" + DOT + r"\d)\)$")

def pct(s):
    m = PCT.match(s)
    assert m, s
    v, lo, hi = (x.replace(DOT, ".") for x in m.groups())
    return m.group(1) + "%", v, lo, hi, s[len(m.group(1)) + 1:].strip()

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

def main():
    xml_path, out = sys.argv[1:3]
    assert sha(xml_path) == XML_SHA
    root = ET.parse(xml_path).getroot()
    t2, t3 = table(root, "Table 2:"), table(root, "Table 3:")
    assert t2[0] == ["", "Raw data", "With logical imputation of missing values"]
    assert t2[1] == ["", "Evaluable episodes", "Positive", "Sensitivity", "Evaluable episodes", "Positive", "Sensitivity"]
    assert t3[0] == ["", "Negative (n=162)", "Specificity"]
    R, claims = [], []

    def add(id_, kind, name, desc, attrs, links=(), src=(SRC,), facets=FACETS):
        R.append({"id": id_, "kind": kind, "name": name, "description": desc, "status": "needs_review",
                  "facets": dict(facets), "source_ids": list(src),
                  "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attrs})

    def rev(note, method="deterministic-table-parse"):
        return {"method": [method], "reviewer": ["claude"],
                "reviewer_note": "Extracting Claude research agent (uc-pathogens); not an independent review",
                "date": DATE, "artifact_sha256": XML_SHA, "retrieval_url": URL, "note": note + " Pending independent review."}
    PNOTE = "Extracted by deterministic parse of the pinned Europe PMC full-text XML (extract/extract_wolf2026.py), with row and column labels asserted. printed_value is the cell text exactly."

    def res(rid, eval_id, metric, unit, direction, printed, numeric, qual, loc, unc=None, unit_detail=None, num=None, den=None):
        attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed, "numeric_value": numeric,
                 "metric_qualifier": qual, "source_locator": loc}
        if unit_detail:
            attrs["unit_detail"] = unit_detail
        if num is not None:
            attrs["numerator"], attrs["denominator"] = num, den
        if unc:
            attrs["uncertainty"] = unc
        else:
            attrs["missing_metadata"] = {"uncertainty": {"reason": "inapplicable", "note": "Count"}}
        attrs["review"] = rev(PNOTE)
        add(rid, "result", rid.replace(P + "-result-", "wolf2026 "), "Reported measurement transcribed from the pinned source. Not independently reproduced.",
            attrs, links=[("evaluation", eval_id)], facets={})
        claims.append([rid, SRC, loc, printed, "result"])

    groups = [("All bloodstream infection episodes (n=94)", "all", "all bloodstream infection episodes"),
              ("Bacterial bloodstream infections (n=91)", "bacterial", "bacterial bloodstream infections"),
              ("Common bloodstream infection pathogens (n=87)", "common", "common bloodstream infection pathogens")]
    periods = [("Prediction (day −3 to −1)", "prediction"), ("Diagnosis (day 0 or 1)", "diagnosis")]
    i = 2
    for gi, (glabel, gkey, gname) in enumerate(groups):
        if gi:
            assert t2[i] == [""], t2[i]; i += 1
        assert t2[i][0] == glabel and all(x == "" for x in t2[i][1:]), t2[i]; i += 1
        for plabel, pkey in periods:
            r = t2[i]; i += 1
            assert r[0] == plabel and len(r) == 7, r
            ev = f"{P}-eval-{pkey}"
            for off, mkey, mname in [(1, "raw", "raw data"), (4, "imputed", "with logical imputation of missing values")]:
                base = f"Table 2, group '{glabel}', row '{plabel}', block '{'Raw data' if mkey == 'raw' else 'With logical imputation of missing values'}'"
                q = f"{gname}; {mname}; reference: organisms identified by blood culture"
                res(f"{P}-result-{pkey}-{gkey}-{mkey}-evaluable", ev, "count", "count", "unknown", r[off], r[off],
                    f"evaluable episodes; {q}", f"{base}, column 'Evaluable episodes'", unit_detail="bloodstream infection episodes")
                res(f"{P}-result-{pkey}-{gkey}-{mkey}-positive", ev, "true-positive-count", "count", "higher", r[off + 1], r[off + 1],
                    f"episodes with all culture organisms detected; {q}", f"{base}, column 'Positive'", unit_detail="bloodstream infection episodes")
                pv, v, lo, hi, ci = pct(r[off + 2])
                res(f"{P}-result-{pkey}-{gkey}-{mkey}-sensitivity", ev, "recall", "percent", "higher", pv, v,
                    f"episode-level {'predictive' if pkey == 'prediction' else 'diagnostic'} sensitivity; {q}", f"{base}, column 'Sensitivity'",
                    unc={"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "printed": ci},
                    num=int(r[off + 1]), den=int(r[off]))
    assert i == len(t2)
    # Table 3
    rows3 = t3[1:]
    expect = [["Any organism*", "", ""], None, None, [""], ["Common bloodstream infection pathogen‡", ""], None, None]
    assert len(rows3) == 7 and rows3[0] == expect[0] and rows3[3] == expect[3] and rows3[4] == expect[4], rows3
    for gi, gkey, glabel, gname in [(1, "any", "Any organism*", "any bacterium or yeast (Burkholderia, moulds, viruses and parasites excluded)"),
                                    (5, "common", "Common bloodstream infection pathogen‡", "common bloodstream infection pathogens")]:
        for off, ckey, clabel in [(0, "all", "All positive tests"), (1, "cutoff140", "≥140 molecules per μL†")]:
            r = rows3[gi + off]
            assert r[0] == clabel and len(r) == 3, r
            ev = f"{P}-eval-specificity-{ckey}"
            base = f"Table 3, group '{glabel}', row '{clabel}'"
            q = f"{gname}; control samples without fever or infection within 7 days"
            res(f"{P}-result-specificity-{gkey}-{ckey}-negative", ev, "true-negative-count", "count", "higher", r[1], r[1],
                f"negative control samples; {q}", f"{base}, column 'Negative (n=162)'", unit_detail="control samples", )
            pv, v, lo, hi, ci = pct(r[2])
            res(f"{P}-result-specificity-{gkey}-{ckey}-specificity", ev, "specificity", "percent", "higher", pv, v,
                f"predictive specificity; {q}", f"{base}, column 'Specificity'",
                unc={"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "printed": ci}, num=int(r[1]), den=162)

    add(SRC, "source", "Predicting bloodstream infection by plasma cell-free metagenomic sequencing: a prospective cohort study",
        "Primary source retrieved and hashed for the 2026-10-11 DNA pathogen-identification literature pass.",
        {"url": "https://doi.org/10.1016/j.lanmic.2025.101312", "artifact_url": URL,
         "version": "The Lancet Microbe 7:101312, published online 2026-03-02; PMC13154368 full-text XML (author manuscript)",
         "retrieved_at": "2026-10-11T22:07:34Z", "artifact_sha256": XML_SHA, "doi": "10.1016/j.lanmic.2025.101312",
         "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml", "venue": "The Lancet Microbe", "year": 2026,
         "source_locator": "Licence statement in the article XML <license> element: CC BY 4.0"},
        src=())
    add(f"{P}-service-karius", "service", "Karius plasma microbial cell-free DNA sequencing (mcfDNA-Seq)",
        "Plasma microbial cell-free DNA metagenomic sequencing run in a CLIA-accredited and CAP-accredited laboratory (Karius, Redwood City, CA) against a proprietary reference-genome database, reporting molecules per microlitre for each organism.",
        {"reported_name": "mcfDNA-Seq", "entity_level": "service",
         "access": "Commercial laboratory test; reference database proprietary (Methods 'Procedures' paragraph 2; appendix pp 2-3, not inspected)"},
        facets={**FACETS, "method_types": ["conventional_pipeline"]})
    cfgs = {"all": ("All positive tests", "Any organism reported by the laboratory counts as positive."),
            "cutoff140": ("Post-hoc 140 molecules per microlitre cut-off", "Only organisms reported at 140 molecules per microlitre of plasma or higher count as positive; cut-off chosen post hoc by maximising Youden's index on the consolidated data (AUC 0.73).")}
    for k, (name, params) in cfgs.items():
        add(f"{P}-config-{k}", "configuration", f"Karius mcfDNA-Seq, {name.lower()} (Wolf et al. 2026)", f"Karius mcfDNA-Seq results interpreted with: {name.lower()}.",
            {"reported_name": name, "parameters": params, "foundation_model_eligible": False,
             "access_reuse": "Commercial laboratory test; testing was provided by Karius as non-financial support",
             "source_locator": "Methods 'Statistical analysis' paragraphs 3 and 5; Table 3 footnote",
             "missing_metadata": {"version": {"reason": "unreported", "note": "No assay, pipeline or database version is given in the inspected text"}}},
            links=[("configuration_of", f"{P}-service-karius")], facets={**FACETS, "method_types": ["conventional_pipeline"]})
    datasets = {
        "bsi": ("Bloodstream infection episodes in children and young people with high-risk leukaemia (Wolf et al. 2026)",
                "94 bloodstream infection episodes (pilot and completion phases) in patients under 25 receiving leukaemia care at St Jude Children's Research Hospital, 2017-2022; leftover plasma from day -7 to day +1",
                "Methods 'Study design and participants'; Table 1; Table 2"),
        "controls": ("Control plasma samples without fever or infection (Wolf et al. 2026)",
                     "162 control samples from the same population with no fever or infection within 7 days before or after collection",
                     "Methods 'Procedures' paragraph 1; Table 3"),
    }
    for k, (name, pop, loc) in datasets.items():
        add(f"{P}-data-{k}", "dataset", name, "Prospectively collected leftover clinical plasma samples.",
            {"version": "As described in Wolf et al. 2026 (consolidated pilot and completion phases)", "population": pop, "split": "Single prospective cohort; no split",
             "access": "Not stated in the inspected text", "source_locator": loc})
    bench = f"{P}-benchmark-mcfdna-bsi"
    add(bench, "benchmark", "Plasma mcfDNA sequencing for predicting and diagnosing bloodstream infection in high-risk leukaemia (Wolf et al. 2026)",
        "Episode-level sensitivity against blood-culture organisms before and at bloodstream infection onset, and specificity in afebrile control samples.",
        {"entity_level": "suite", "version": "Lancet Microbe 2026, Tables 2 and 3", "task": "Detect the blood-culture organism in plasma cell-free DNA before and at bloodstream infection onset",
         "source_locator": "Methods 'Outcomes' and 'Statistical analysis'", "scope_note": "Day-by-day sensitivity (Figure 2 and appendix) and the appendix tables were not extracted.",
         "limitations": ["One commercial assay; no comparator workflow."]})
    protos = {
        "prediction": ("Predictive sensitivity, day -3 to -1 (Wolf et al. 2026 Table 2)", "bsi",
                       "Proportion of evaluable bloodstream infection episodes in which all organisms identified by blood culture were detected by mcfDNA-Seq in at least one sample from the 3 days before onset."),
        "diagnosis": ("Diagnostic sensitivity, day 0 or 1 (Wolf et al. 2026 Table 2)", "bsi",
                      "Proportion of evaluable bloodstream infection episodes in which all organisms identified by blood culture were detected by mcfDNA-Seq in at least one sample from the day of or day after onset."),
        "specificity": ("Predictive specificity in control samples (Wolf et al. 2026 Table 3)", "controls",
                        "Proportion of evaluable control samples in which mcfDNA-Seq detected no bacterium or yeast (any organism) or no common bloodstream infection pathogen."),
    }
    for k, (name, dk, proto) in protos.items():
        pattrs = {"protocol": proto + " Raw data and logical imputation of missing values are both reported; 95% CIs as printed. The laboratory was masked to sample status.",
                  "version": "Table 2", "source_locator": "Methods 'Outcomes' and 'Statistical analysis' paragraphs 2-5",
                  "limitations": ["Reference for sensitivity is blood culture, which does not identify every infection; polymicrobial episodes count as detected only if every culture organism is found."]}
        if k == "specificity":  # review W2
            pattrs.update({"protocol": "Proportion of evaluable control samples (no fever or documented infection in the 7 days before or after collection) in which mcfDNA-Seq detected no bacterium or yeast (moulds, viruses and parasites excluded a priori; Burkholderia cepacia excluded afterwards for possible local contamination), or no common bloodstream infection pathogen; with all positive tests and with the post-hoc 140 molecules per microlitre cut-off. 95% CIs as printed. The laboratory was masked to sample status.",
                           "version": "Table 3",
                           "limitations": ["Control samples come from the same high-risk leukaemia population and are not patients tested for suspected infection.", "The 140 molecules per microlitre cut-off was chosen post hoc by maximising Youden's index on the consolidated data."]})
        add(f"{P}-protocol-{k}", "protocol", name, proto, pattrs,
            links=[("uses_data", f"{P}-data-{dk}"), ("part_of", bench)])
    evals = {"prediction": ("all", "prediction"), "diagnosis": ("all", "diagnosis"), "specificity-all": ("all", "specificity"), "specificity-cutoff140": ("cutoff140", "specificity")}
    for ek, (ck, pk) in evals.items():
        lim = ["Testing was provided by Karius, whose representatives took part in sample processing, analysis and data management, and one author is a Karius employee (Declaration of interests; Role of the funding source)."]
        if ck == "cutoff140":
            lim.append("Post-hoc: the 140 molecules per microlitre cut-off was chosen on the same consolidated data, so the specificity is optimistic.")
        add(f"{P}-eval-{ek}", "evaluation", f"Karius mcfDNA-Seq ({cfgs[ck][0].lower()}) on {protos[pk][0]}", "Published prospective cohort result; transcribed, not reproduced.",
            {"origin": "author_reported", "protocol": f"{P}-protocol-{pk}", "version": "Primary source as retrieved 2026-10-11",
             "comparison": {"protocol_id": f"{P}-protocol-{pk}", "dataset_version": datasets[protos[pk][1]][0], "split": "Single cohort",
                            "population": datasets[protos[pk][1]][1], "inputs": "Leftover clinical plasma, microbial cell-free DNA",
                            "adaptation": cfgs[ck][1], "metric_implementation": protos[pk][2],
                            "aggregation": "Episodes (Table 2) or control samples (Table 3), raw or with logical imputation as printed", "budget": None},
             "source_locator": "Table 2" if pk != "specificity" else f"Table 3, rows '{'All positive tests' if ck == 'all' else '≥140 molecules per μL†'}'",
             "limitations": lim},
            links=[("system", f"{P}-config-{ck}"), ("assessment", f"{P}-protocol-{pk}"), ("data", f"{P}-data-{protos[pk][1]}")])
    common_lims = ["Single commercial assay (Karius); no comparator workflow on the same samples.",
                   "Karius provided testing and took part in sample processing and analysis, data management and manuscript review; one author (AAA) is a Karius employee and coinventor on a pending Karius patent, and two others report research or sequencing support from Karius.",
                   "Paediatric and young-adult high-risk leukaemia population; not a general sepsis-alert population.",
                   "Reference for sensitivity is blood culture."]
    judg = {
        "diagnosis": ("proxy", 1, "Diagnostic sensitivity of the Karius plasma cell-free DNA assay against blood-culture organisms at bloodstream infection onset matches the use case's inputs and endpoint (agreement with blood culture for plasma microbial cell-free DNA), measured prospectively in a second population. It is proxy evidence for the same reason as the Karius anchor: blood culture does not identify every infection, so this is agreement with culture, not sensitivity against all infections. The population is children and young adults with high-risk leukaemia, and Karius took part in processing and analysis.",
                      "Episode-level diagnostic sensitivity (day 0 or 1) against all blood-culture organisms, raw and with imputation, overall, bacterial and common pathogens"),
        "prediction": ("proxy", 2, "Detection of the blood-culture organism in plasma cell-free DNA in the three days before onset bears on the assay's detection limits in the use case's specimen, but prediction before clinical presentation is a different decision from diagnostic testing. Proxy evidence.",
                       "Episode-level predictive sensitivity (day -3 to -1) against all blood-culture organisms, raw and with imputation"),
        "specificity": ("proxy", 3, "Detections in control plasma from patients without fever or infection measure background and clinically false-positive signal, which bears on the use case's contamination question. Proxy evidence: afebrile controls rather than patients tested for suspected infection.",
                        "Predictive specificity in 162 control samples for any bacterium or yeast and for common bloodstream infection pathogens, with all positive tests and with a post-hoc 140 molecules per microlitre cut-off"),
    }
    for pk, (relv, order, rationale, endpoint) in judg.items():
        pid = f"{P}-protocol-{pk}"
        extra = []
        if pk == "specificity":
            extra.append("The 140 molecules per microlitre cut-off is post hoc (Youden index on the same data).")
            extra.append("Burkholderia was excluded after the fact because of possible local sample contamination (Methods 'Statistical analysis').")
        add(f"use-case-mapping-dna-pathogen-20261011-wolf2026-{pk}", "claim",
            f"Relevance of {protos[pk][0]} to \"Select a DNA pathogen-identification workflow for diagnostic testing\"", rationale,
            {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": relv, "endpoint": endpoint, "rationale": rationale,
             "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                             "Do not combine these results with another protocol's results; reference standards, specimens and scoring units differ between sources."],
             "limitations": common_lims + extra,
             "citation_locators": [{"source_id": SRC, "locator": "Table 2; Table 3; Methods 'Outcomes' and 'Statistical analysis'"}],
             "source_locator": f"{SRC}: {'Table 3' if pk == 'specificity' else 'Table 2'}", "revision": 1,
             "reason": "Recorded from the 2026-10-11 DNA pathogen-identification literature pass (data/omics/use-case-coverage-dna-pathogen-20261011-wolf2026). Needs independent review.",
             "comparison_group": "wolf2026-plasma-mcfdna", "comparison_title": "Karius plasma mcfDNA sequencing in high-risk paediatric leukaemia (Wolf et al. 2026)",
             "headline_metric": "specificity" if pk == "specificity" else "recall",
             "stratum_label": {"diagnosis": "Diagnosis (day 0 or 1)", "prediction": "Prediction (day -3 to -1)", "specificity": "Control samples"}[pk], "stratum_order": order,
             "review": rev("Judgement drafted by the extracting agent from the pinned article.", method="transcription")},
            links=[("subject", UC)], facets={})
    add(f"{P}-claim-developer-involvement", "claim", f"developer_involvement: {P}-service-karius", "Descriptive fact transcribed from the pinned source.",
        {"field": "developer_involvement",
         "value": "Karius provided mcfDNA-Seq testing as non-financial support, and its representatives were involved in sample processing and analysis, data management and reviewing the manuscript, but not in its preparation, writing or approval or in the decision to submit.",
         "source_locator": "Role of the funding source; Acknowledgments", "review": rev("Transcribed from the pinned article XML text.", method="transcription")},
        links=[("subject", f"{P}-service-karius")], facets={})
    claims.append([f"{P}-claim-developer-involvement", SRC, "Role of the funding source; Acknowledgments", R[-1]["attributes"]["value"], "claim"])

    finalize(R)
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
