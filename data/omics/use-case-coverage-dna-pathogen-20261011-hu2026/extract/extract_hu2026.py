"""Extract Hu et al. 2026 (Microbiol Spectr 14:e03993-25) Table 2 and Supplemental Tables S6 and S7.

Usage: python3 -I extract_hu2026.py <PMC13339908.xml> <spectrum.03993-25-s0001.docx> <batch-folder>

Deterministic parse of the pinned Europe PMC full-text XML (Table 2) and the pinned
supplementary DOCX (Tables S6 and S7, the fifth and sixth tables in the document).
Every row and column label is asserted before a value is used. Writes batch.jsonl and
claims.csv into the batch folder. Records are needs_review; this script never marks
anything reviewed.
"""
import csv, hashlib, json, re, sys, zipfile
import xml.etree.ElementTree as ET

XML_SHA = "555995fd870d878dd0e6c112064bbf1d2535a1cb1af17f70570ecc11774caa2d"
DOCX_SHA = "7ab6c2cde30619e506a5e015ef5bbb253dfa6359ebd56140577eef136b153ed9"
P = "dna-pathogen-20261011-hu2026"
SRC = f"{P}-source"
SRC_SUPP = f"{P}-source-supp"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13339908/fullTextXML"
SUPP_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13339908/supplementaryFiles"
DATE = "2026-10-11"
FACETS = {"areas": ["microbes-communities"], "contexts": ["clinical_research"]}
PLUS, MINUS = "＋", "−"

def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()

def txt(e):
    return re.sub(r"\s+", " ", "".join(e.itertext())).strip()

def table2(xml_path):
    root = ET.parse(xml_path).getroot()
    tw = [t for t in root.iter("table-wrap") if txt(t.find("label")) == "TABLE 2"]
    assert len(tw) == 1
    rows = [[txt(c) for c in r] for r in tw[0].iter("tr")]
    assert rows[0] == ["", "Culture", "Clinical microbiological tests (CMT)", "Composite reference standard (CRS)"], rows[0]
    return rows

def docx_tables(path):
    x = zipfile.ZipFile(path).read("word/document.xml").decode()
    out = []
    for tbl in re.findall(r"<w:tbl>.*?</w:tbl>", x, re.S):
        rows = []
        for r in re.findall(r"<w:tr[ >].*?</w:tr>", tbl, re.S):
            rows.append(["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", c)).strip() for c in re.findall(r"<w:tc>.*?</w:tc>", r, re.S)])
        out.append(rows)
    paras = ["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)) for p in re.findall(r"<w:p[ >].*?</w:p>", re.sub(r"<w:tbl>.*?</w:tbl>", "", x, flags=re.S), re.S)]
    return out, [p for p in paras if p.strip()]

REFS = [("culture", "Culture", "routine culture"), ("cmt", "Clinical microbiological tests (CMT)", "clinical microbiological tests (CMT)"), ("crs", "Composite reference standard (CRS)", "composite reference standard (CRS)")]
WF = [("mgi", "NGS", "MGI short-read workflow"), ("hdont", "TGS", "host-depleted ONT workflow")]

def parse_main(rows):
    """Return {(wf, ref): {tp, fp, fn, tn, ppa, npa}} with printed strings and locators."""
    out = {}
    for wi, (wkey, wlabel, _) in enumerate(WF):
        b = rows[1 + wi * 5: 6 + wi * 5]
        assert b[0][0] == wlabel and b[0][2:] == [PLUS, MINUS] * 3, b[0]
        assert b[1][0] == PLUS and b[2][0] == MINUS, (b[1][0], b[2][0])
        assert [b[3][i] for i in (1, 3, 5)] == ["PPA"] * 3 and [b[4][i] for i in (1, 3, 5)] == ["NPA"] * 3
        for ri, (rkey, rlabel, _) in enumerate(REFS):
            c = 1 + 2 * ri
            loc = f'Table 2, block "{wlabel}", column group "{rlabel}"'
            out[(wkey, rkey)] = {
                "tp": (b[1][c], f'{loc}, row "{PLUS}" (sequencing positive), column "{PLUS}" (comparator positive)'),
                "fp": (b[1][c + 1], f'{loc}, row "{PLUS}" (sequencing positive), column "{MINUS}" (comparator negative)'),
                "fn": (b[2][c], f'{loc}, row "{MINUS}" (sequencing negative), column "{PLUS}" (comparator positive)'),
                "tn": (b[2][c + 1], f'{loc}, row "{MINUS}" (sequencing negative), column "{MINUS}" (comparator negative)'),
                "ppa": (b[3][c + 1], f'{loc}, row "PPA"'),
                "npa": (b[4][c + 1], f'{loc}, row "NPA"'),
            }
    return out

def parse_supp(rows, table_name):
    """Tables S6/S7: two blocks (NGS, TGS) of 8 rows."""
    out = {}
    assert len(rows) == 16, len(rows)
    for wi, (wkey, wlabel, _) in enumerate(WF):
        b = rows[wi * 8: wi * 8 + 8]
        assert b[0][0] == wlabel and b[0][1] == "Culture" and b[0][2].startswith("Clinical microbiological tests") and b[0][3].startswith("Composite reference"), b[0]
        assert [x for x in b[2] if x] == [PLUS, MINUS] * 3, b[2]
        assert b[3][1] == PLUS and b[4][1] == MINUS
        labels6, labels7 = [b[6][i] for i in (2, 5, 8)], [b[7][i] for i in (2, 5, 8)]
        assert labels6 == ["Sensitivity", "PPA", "PPA"] and labels7 == ["Specificity", "NPA", "NPA"], (labels6, labels7)
        for ri, (rkey, rlabel, _) in enumerate(REFS):
            c = 2 + 3 * ri
            loc = f'{table_name}, block "{wlabel}", column group "{rlabel}"'
            pl, nl = labels6[ri], labels7[ri]
            out[(wkey, rkey)] = {
                "tp": (b[3][c], f'{loc}, row "{PLUS}" (sequencing positive), column "{PLUS}" (comparator positive)'),
                "fp": (b[3][c + 1], f'{loc}, row "{PLUS}" (sequencing positive), column "{MINUS}" (comparator negative)'),
                "fn": (b[4][c], f'{loc}, row "{MINUS}" (sequencing negative), column "{PLUS}" (comparator positive)'),
                "tn": (b[4][c + 1], f'{loc}, row "{MINUS}" (sequencing negative), column "{MINUS}" (comparator negative)'),
                "ppa": (b[6][c + 1], f'{loc}, row "{pl}"'),
                "npa": (b[7][c + 1], f'{loc}, row "{nl}"'),
            }
    return out

def num(s):
    s = s.replace("%", "").strip()
    assert re.fullmatch(r"\d+(\.\d+)?", s), s
    return s

UC = "use-case-diagnostic-dna-pathogen-identification"
CORE_LIMITS = [
    "Organism-level agreement in 62 residual BALF specimens from lower respiratory tract infection; not plasma cell-free DNA and not patient-level diagnosis.",
    "The two workflows differ in platform, library preparation, host depletion, aligner and positivity threshold together (MGISEQ-200 with BWA-MEM and RP20M >= 3; host-depleted ONT GridION with minimap2 and RP10K >= 1), so the comparison is of whole workflows, not of classifiers.",
    "Both workflows used the same curated 20,484-genome reference database and lowest-common-ancestor assignment.",
    "Eight of the listed authors, including co-corresponding author Lifeng Li, are affiliated with Genskey Medical Technology (Beijing), a clinical mNGS provider; the article states that the authors declare no conflict of interest. The workflows are the authors' own, so the evaluations are author_reported.",
]

DISCREPANT = "Discrepant analysis: confirmatory qPCR or GeneXpert was run on discordant sequencing-positive findings where residual BALF allowed (19 NGS-positive and 17 TGS-positive findings confirmed), so the CMT reference depends partly on the sequencing results and favours the sequencing workflows."

def review_obj(art_sha, url, note):
    return {"method": ["transcription"], "reviewer": ["claude"],
            "reviewer_note": "Extracting Claude research agent (uc-pathogens); not an independent review",
            "date": DATE, "artifact_sha256": art_sha, "retrieval_url": url,
            "note": note + " Pending independent review."}

def build_entities(docx_sha):
    R = []
    def add(id_, kind, name, desc, attrs, links=(), src=(SRC,), facets=FACETS):
        R.append({"id": id_, "kind": kind, "name": name, "description": desc, "status": "needs_review",
                  "facets": dict(facets), "source_ids": list(src),
                  "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attrs})
    add(SRC, "source", "Benchmarking next- versus third-generation sequencing in metagenomics: performance metrics and diagnostic efficacy",
        "Primary source retrieved and hashed for the 2026-10-11 DNA pathogen-identification literature pass.",
        {"url": "https://doi.org/10.1128/spectrum.03993-25", "artifact_url": XML_URL,
         "version": "Microbiology Spectrum 14(7):e03993-25, published 2026-06-03; PMC13339908 full-text XML",
         "retrieved_at": "2026-10-11T21:37:24Z", "artifact_sha256": XML_SHA, "doi": "10.1128/spectrum.03993-25",
         "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml",
         "venue": "Microbiology Spectrum", "year": 2026,
         "source_locator": "Licence statement in the article XML <license> element: Creative Commons Attribution 4.0"},
        src=())
    add(SRC_SUPP, "source", "Hu et al. 2026 Supplemental Tables S1 to S4, S6 and S7 (spectrum.03993-25-s0001.docx)",
        "Supplementary file of the primary source, retrieved and hashed for the 2026-10-11 DNA pathogen-identification literature pass.",
        {"url": "https://doi.org/10.1128/spectrum.03993-25", "artifact_url": SUPP_URL,
         "version": "spectrum.03993-25-s0001.docx as distributed with PMC13339908",
         "retrieved_at": "2026-10-11T21:41:40Z", "artifact_sha256": docx_sha, "doi": "10.1128/spectrum.03993-25",
         "publication_status": "peer_reviewed", "licence": "CC-BY-4.0",
         "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
         "venue": "Microbiology Spectrum", "year": 2026,
         "retrieval_note": "Europe PMC returns the supplementary files as a ZIP that is rebuilt on each request, so the ZIP hash changes between downloads; artifact_sha256 is the hash of the DOCX member, which was the same in two downloads.",
         "source_locator": "Article XML <supplementary-material> 'Supplemental tables spectrum.03993-25-s0001.docx Tables S1 to S4, S6 and S7'; licence as for the article"},
        src=())
    add(f"{P}-method-harmonised-mngs", "method", "Harmonised mNGS analysis workflow (Hu et al. 2026)",
        "Host removal against GRCh38 plus plasmids, alignment of non-host reads to a curated 20,484-genome microbial database and lowest-common-ancestor assignment, with platform-specific normalised read-count thresholds and a historical negative-control background filter.",
        {"reported_name": "harmonized analytic framework", "entity_level": "method",
         "source_locator": "Methods 'Bioinformatic processing and taxonomic assignment', 'Reference database curation' and 'Read normalization, reporting threshold, and contamination control'",
         "access": "Not stated; no code or database release is named in the article",
         "missing_metadata": {"version": {"reason": "unreported", "note": "No software or database version is given for the workflow as a whole"}}},
        facets={**FACETS, "method_types": ["conventional_pipeline"]})
    cfgs = {
        "mgi": ("MGISEQ-200 short-read mNGS workflow (Hu et al. 2026)", "NGS (MGI platform)", "NGS",
                "Bead beating and TIANGEN Microsample Genomic DNA extraction; VAHTS Universal Plus DNA library for MGI; MGISEQ-200 single-end 50 bp; DUST and quality filtering; Bowtie2 host removal against GRCh38 plus plasmids; BWA-MEM to the curated database; LCA; positive if RP20M >= 3; contaminants flagged above the 95th percentile of historical negative controls",
                "Methods 'NGS workflows', 'Bioinformatic processing and taxonomic assignment' and 'Read normalization, reporting threshold, and contamination control'; Results 'Diagnostic performance for clinical samples' paragraph 1"),
        "hdont": ("Host-depleted ONT GridION mNGS workflow (Hu et al. 2026)", "TGS (HD-ONT)", "TGS",
                  "Host depletion with heat-labile salt-active nuclease and saponin, 17,000 x g centrifugation, bead beating and the same DNA extraction kit; ONT Rapid PCR Barcoding Kit SQK-RPB004; GridION X5 with R9.4.1 flow cells; Guppy basecalling; reads Q > 7 and > 200 bp; minimap2 host removal and alignment to the curated database; LCA; positive if RP10K >= 1; same contamination filter",
                  "Methods 'TGS workflows', 'Bioinformatic processing and taxonomic assignment' and 'Read normalization, reporting threshold, and contamination control'; Results 'Diagnostic performance for clinical samples' paragraph 1"),
    }
    for k, (name, rep, _, params, loc) in cfgs.items():
        add(f"{P}-config-{k}", "configuration", name, f"{rep} as run on the clinical BALF specimens in Hu et al. 2026.",
            {"reported_name": rep, "source_locator": loc, "foundation_model_eligible": False, "parameters": params,
             "access_reuse": "Laboratory workflow described in the article; not released as software",
             "missing_metadata": {"version": {"reason": "unreported", "note": "Guppy, Bowtie2, BWA-MEM and minimap2 versions and the database build date are not stated"}}},
            links=[("configuration_of", f"{P}-method-harmonised-mngs")], facets={**FACETS, "method_types": ["conventional_pipeline"]})
    data_id = f"{P}-data-balf62"
    add(data_id, "dataset", "62 residual BALF specimens with culture results (Hu et al. 2026)",
        "Residual bronchoalveolar lavage fluid specimens with traceable culture results, sequenced by both clinical workflows.",
        {"version": "As described in Hu et al. 2026",
         "population": "62 BALF specimens, primarily from lower respiratory tract infection; per workflow, Table 2 counts 77 organism results against culture, 96 against CMT and 133 against CRS",
         "split": "Single clinical set; no split", "denominator": 62,
         "access": "Not stated in the inspected text",
         "source_locator": "Methods 'Clinical performance evaluation and reference standards' paragraph 1; Results 'Diagnostic performance for clinical samples' paragraph 1; Discussion limitations paragraph"})
    bench = f"{P}-benchmark-ngs-tgs-balf"
    add(bench, "benchmark", "Short-read versus host-depleted nanopore mNGS on BALF (Hu et al. 2026)",
        "Two clinical metagenomic workflows scored at organism level against culture, clinical microbiological tests and a composite reference standard.",
        {"entity_level": "suite", "version": "Microbiology Spectrum 2026, Table 2 and Supplemental Tables S6 and S7",
         "task": "Detect organisms in a BALF specimen and agree with a reference standard",
         "source_locator": "Methods 'Clinical performance evaluation and reference standards'; Results 'Diagnostic performance for clinical samples'",
         "scope_note": "Mock-community results (Supplemental Tables S1 and S2, Figures 2 and 3) are per-organism rows and prose aggregates and were not extracted.",
         "limitations": ["Organism-level agreement, not patient-level diagnosis."]})
    refdef = {
        "culture": ("routine culture", "Routine culture, which includes only culturable microorganisms.", "Culture"),
        "cmt": ("clinical microbiological tests (CMT)", "Culture plus additional verification: organism-specific qPCR, or Xpert MTB/RIF for M. tuberculosis complex, on discordant organisms where residual BALF allowed.", "Clinical microbiological tests (CMT)"),
        "crs": ("composite reference standard (CRS)", "CMT plus organisms that lacked targeted testing but were detected by both sequencing workflows under the reporting criteria (31 organisms added).", "Composite reference standard (CRS)"),
    }
    order = {"culture": 1, "cmt": 2, "crs": 3}
    for rk, (rname, rtext, rlabel) in refdef.items():
        pid = f"{P}-protocol-{rk}"
        lim = ["Organism-level agreement; a specimen contributes one comparison per organism detected by either side."]
        if rk == "crs":
            lim.append("Incorporation bias: organisms detected by both sequencing workflows were added to the reference, so PPA and NPA against the CRS favour the sequencing workflows by construction.")
        if rk == "culture":
            lim.append("Culture recovers only culturable organisms, so most sequencing-only detections count as false positives against it.")
        if rk == "cmt":
            lim.append(DISCREPANT)  # review H2
        add(pid, "protocol", f"Organism-level agreement with {rname}, 62 BALF specimens (Hu et al. 2026)",
            f"Positive and negative percent agreement of each workflow's organism calls against {rname}, for all organisms (Table 2), bacteria (Supplemental Table 6) and fungi (Supplemental Table 7).",
            {"protocol": f"Reference: {rtext} Each organism result is concordant positive, sequencing positive and comparator negative, sequencing negative and comparator positive, or concordant negative; PPA = TP/(TP+FN) and NPA = TN/(TN+FP). Supplemental Tables S6 and S7 label the culture column 'Sensitivity' and 'Specificity'.",
             "version": "Table 2; Supplemental Tables S6 and S7",
             "source_locator": "Methods 'Clinical performance evaluation and reference standards' paragraphs 1-3; Table 2 footnote",
             "limitations": lim},
            links=[("uses_data", data_id), ("part_of", bench)], src=(SRC, SRC_SUPP))
        for wk in ("mgi", "hdont"):
            add(f"{P}-eval-{rk}-{wk}", "evaluation", f"{cfgs[wk][0]} against {rname}",
                "Published clinical mNGS workflow comparison; transcribed, not reproduced.",
                {"origin": "author_reported", "protocol": pid, "version": "Primary source as retrieved 2026-10-11",
                 "comparison": {"protocol_id": pid, "dataset_version": "62 residual BALF specimens (Hu et al. 2026)", "split": "Single clinical set",
                                "population": "Organisms detected in the 62 BALF specimens by the workflow or the reference", "inputs": "DNA extracted from BALF",
                                "adaptation": "Workflow as stated per configuration", "metric_implementation": "Organism-level 2x2 counts; PPA and NPA",
                                "aggregation": "All organism results in the specimen set", "budget": None},
                 "source_locator": f"Table 2, block '{cfgs[wk][2]}', column group '{rlabel}'; Supplemental Tables S6 and S7, same block and column group",
                 "limitations": CORE_LIMITS},
                links=[("system", f"{P}-config-{wk}"), ("assessment", pid), ("data", data_id)], src=(SRC, SRC_SUPP))
        endpoint = f"Organism-level PPA and NPA (with 2x2 counts) of a short-read MGI workflow and a host-depleted ONT workflow against {rname} in 62 BALF specimens, for all organisms, bacteria and fungi"
        rationale = ("Two complete clinical DNA mNGS workflows are compared on the same patient specimens against a stated reference standard, which bears on the use case's question of which workflow detects clinically relevant pathogens. "
                     "It is proxy evidence: the specimens are BALF rather than plasma cell-free DNA, agreement is counted per organism rather than per patient, and the two workflows differ in platform, host depletion, aligner and threshold together.")
        lims = list(CORE_LIMITS) + lim
        if rk == "cmt":
            lims.remove(DISCREPANT)
            lims.append("The HD-ONT NPA against CMT is printed as 79.2% in Table 2 and Results, but the same block's counts give 42/52 = 80.8% (result source_anomaly).")
            lims.append(DISCREPANT)  # review H2
        if rk == "crs":
            lims.append("The use case's exclusion of sensitivity against a composite or adjudicated reference was recorded for the Karius source's composite endpoint; this composite reference from a different source is recorded as proxy evidence only, because it is built partly from the scored workflows' own calls.")  # review H3
        add(f"use-case-mapping-dna-pathogen-20261011-hu2026-{rk}", "claim",
            f"Relevance of organism-level agreement with {rname}, 62 BALF specimens (Hu et al. 2026) to \"Select a DNA pathogen-identification workflow for diagnostic testing\"",
            rationale,
            {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": "proxy", "endpoint": endpoint, "rationale": rationale,
             "constraints": ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
                             "Do not combine these results with another protocol's results; reference standards, specimens and scoring units differ between sources."],
             "limitations": lims,
             "citation_locators": [{"source_id": SRC, "locator": "Table 2; Methods 'Clinical performance evaluation and reference standards'"},
                                   {"source_id": SRC_SUPP, "locator": "Supplemental Tables S6 and S7"}],
             "source_locator": f"{SRC}: Table 2; {SRC_SUPP}: Supplemental Tables S6 and S7",
             "revision": 1,
             "reason": "Recorded from the 2026-10-11 DNA pathogen-identification literature pass (data/omics/use-case-coverage-dna-pathogen-20261011-hu2026). Needs independent review.",
             "comparison_group": "hu2026-balf-ngs-tgs", "comparison_title": "Short-read versus host-depleted nanopore mNGS on 62 BALF specimens (Hu et al. 2026)",
             "headline_metric": "recall", "stratum_label": rlabel, "stratum_order": order[rk],
             "review": review_obj(XML_SHA, XML_URL, "Judgement drafted by the extracting agent from the pinned article and supplement.")},
            links=[("subject", UC)], src=(SRC, SRC_SUPP), facets={})
    add(f"{P}-claim-crs-incorporation", "claim", f"reference_standard_definition: {P}-protocol-crs",
        "Descriptive fact transcribed from the pinned source.",
        {"field": "reference_standard_definition",
         "value": "The composite reference standard adds to the clinical microbiological tests the organisms that lacked targeted testing results but were detected by both sequencing workflows (MGI and HD-ONT) under the reporting criteria; 31 organisms were added this way.",
         "source_locator": "Methods 'Clinical performance evaluation and reference standards' paragraph 1, third comparator; Results 'Diagnostic performance for clinical samples' paragraph 3",
         "review": review_obj(XML_SHA, XML_URL, "Transcribed from the pinned article XML text.")},
        links=[("subject", f"{P}-protocol-crs")], facets={})
    return R

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
    xml_path, docx_path, out = sys.argv[1:4]
    assert sha(xml_path) == XML_SHA, sha(xml_path)
    docx_sha = sha(docx_path)
    assert docx_sha == DOCX_SHA, docx_sha
    main_rows = table2(xml_path)
    tables, paras = docx_tables(docx_path)
    assert any(p.startswith("Supplemental Table 6") for p in paras) and any(p.startswith("Supplemental Table 7") for p in paras), paras
    blocks = {
        "all": ("Table 2", parse_main(main_rows), SRC, XML_SHA, XML_URL, "all organisms"),
        "bacteria": ("Supplemental Table 6", parse_supp(tables[4], "Supplemental Table 6"), SRC_SUPP, docx_sha, SUPP_URL, "bacteria"),
        "fungi": ("Supplemental Table 7", parse_supp(tables[5], "Supplemental Table 7"), SRC_SUPP, docx_sha, SUPP_URL, "fungi"),
    }
    recs, claims = [], []
    for (rkey, rlabel, rname) in REFS:
        for (wkey, wlabel, wname) in WF:
            eval_id = f"{P}-eval-{rkey}-{wkey}"
            for gkey, (tname, parsed, src, art_sha, url, gname) in blocks.items():
                cells = parsed[(wkey, rkey)]
                is_supp_culture = gkey != "all" and rkey == "culture"
                for k, metric, unit, direction in [
                    ("tp", "true-positive-count", "count", "higher"),
                    ("fp", "false-positive-count", "count", "lower"),
                    ("fn", "false-negative-count", "count", "lower"),
                    ("tn", "true-negative-count", "count", "higher"),
                    ("ppa", "recall", "percent", "higher"),
                    ("npa", "specificity", "percent", "higher"),
                ]:
                    printed, loc = cells[k]
                    if k == "ppa":
                        word = "sensitivity" if is_supp_culture else "positive percent agreement"
                    elif k == "npa":
                        word = "specificity" if is_supp_culture else "negative percent agreement"
                    else:
                        word = {"tp": "concordant positive", "fp": "sequencing positive, comparator negative", "fn": "sequencing negative, comparator positive", "tn": "concordant negative"}[k]
                    qual = f"{word}; organism level; organisms: {gname}; reference: {rname}"
                    rid = f"{P}-result-{rkey}-{wkey}-{gkey}-{k}"
                    attrs = {
                        "metric": metric, "metric_direction": direction, "unit": unit,
                        "printed_value": printed, "numeric_value": num(printed),
                        "metric_qualifier": qual,
                        "source_locator": loc,
                        "missing_metadata": {"uncertainty": {"reason": "unreported"}},
                    }
                    if unit == "count":
                        attrs["unit_detail"] = "organism-level detections (organism in a BALF sample)"
                    if (gkey, wkey, rkey, k) == ("all", "hdont", "cmt", "npa"):
                        attrs["source_anomaly"] = ("Printed 79.2%, also in Results 'Diagnostic performance for clinical samples' paragraph 2. "
                            "The same block's counts give TN 42 and FP 10, so NPA = 42/52 = 80.8%; 79.2% equals 42/53. "
                            "Value kept as printed; needs a reviewer's judgement.")
                    attrs["review"] = {
                        "method": ["deterministic-table-parse"], "reviewer": ["claude"],
                        "reviewer_note": "Extracting Claude research agent (uc-pathogens); not an independent review",
                        "date": DATE, "artifact_sha256": art_sha, "retrieval_url": url,
                        "note": ("Extracted by deterministic parse of the pinned " + ("Europe PMC full-text XML" if gkey == "all" else "supplementary DOCX (word/document.xml)")
                                 + " (extract/extract_hu2026.py), with block, row and column labels asserted. printed_value is the cell text exactly. Pending independent review."),
                    }
                    recs.append({"id": rid, "kind": "result", "name": f"hu2026 {rkey} {wkey} {gkey} {metric}",
                                 "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
                                 "status": "needs_review", "facets": {}, "source_ids": [src],
                                 "links": [{"relation": "evaluation", "target_id": eval_id}], "attributes": attrs})
                    claims.append([rid, src, loc, printed, "result"])
    entities = build_entities(docx_sha)
    finalize(entities + recs)
    allrecs = sorted(entities + recs, key=lambda r: r["id"])
    ids = [r["id"] for r in allrecs]
    assert len(ids) == len(set(ids))
    with open(f"{out}/batch.jsonl", "w") as f:
        for r in allrecs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    for r in entities:
        if r["kind"] == "claim" and not r["attributes"]["field"].startswith("links:"):
            a = r["attributes"]
            claims.append([r["id"], r["source_ids"][0], a.get("source_locator", ""), a.get("value", ""), "claim"])
    with open(f"{out}/claims.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        w.writerows(claims)
    from collections import Counter
    print(dict(Counter(r["kind"] for r in allrecs)), "supplementary DOCX sha256", docx_sha)

if __name__ == "__main__":
    main()
