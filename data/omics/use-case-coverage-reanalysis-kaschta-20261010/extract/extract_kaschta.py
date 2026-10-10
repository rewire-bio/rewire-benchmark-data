"""Deterministic extraction of prose-printed values from Kaschta et al. 2026 (medRxiv), 2026-10-10.

Usage: python3 -I extract_kaschta.py <jats-xml> <batch-dir>

Each result names a paragraph (section path and paragraph number within that section, as
listed by jats_paras.py) and an exact quoted phrase. The script asserts that the phrase occurs
in that paragraph and that the printed value occurs in the phrase, then writes the record.
Figures, Table 1 (an image) and the supplement are not read. No per-patient detail is stored.
"""
import csv, hashlib, json, os, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jats_paras  # noqa: E402
import xml.etree.ElementTree as ET

XML, OUT = sys.argv[1], sys.argv[2]
P = "reanalysis-kaschta-20261010"
UC = "use-case-unresolved-rare-disease-reanalysis"
UC_NAME = "Reanalyse unresolved rare-disease cases"
DATE = "2026-10-10"
FAC = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
SHA = hashlib.sha256(open(XML, "rb").read()).hexdigest()
JATS_URL = "https://www.medrxiv.org/content/early/2026/05/19/2026.05.16.26352295.source.xml"
PARAS = {(path, n): s for path, n, s in jats_paras.paras(ET.parse(XML).getroot())}

records, claims_rows = [], []


def rec(kind, id_, name, description, attributes, source_ids, links=(), facets=None):
    records.append({"id": id_, "kind": kind, "name": name, "description": description, "status": "needs_review",
                    "facets": facets if facets is not None else {}, "source_ids": list(source_ids),
                    "links": [dict(relation=a, target_id=b) for a, b in links], "attributes": attributes})
    return id_


S = f"{P}-source-kaschta2026"
rec("source", S, "Automated versus manual reanalysis in rare disease genomics", "Preprint retrieved and hashed for the reanalysis follow-up pass. Not archived: all rights reserved.",
    {"url": "https://doi.org/10.64898/2026.05.16.26352295", "artifact_url": JATS_URL, "doi": "10.64898/2026.05.16.26352295",
     "version": "medRxiv 2026.05.16.26352295 v1, posted 2026-05-19; JATS source XML", "retrieved_at": "2026-10-10T06:04:35Z", "artifact_sha256": SHA,
     "publication_status": "preprint", "licence": "All rights reserved (medRxiv licence 'cc_no')", "media_type": "application/xml",
     "access_note": "The copyright holder reserves all rights; the artifact is pinned by hash and not archived. The per-patient supplement (352295_file02.xlsx) was not downloaded.",
     "hash_scope": "SHA-256 of the JATS source XML as returned on 2026-10-10."},
    [], facets=FAC)

# ---------------------------------------------------------------- methods and configurations
TALOS = "uc-clinical-20260930-method-talos"
MANUAL = rec("method", f"{P}-method-manual-diagnostic-reanalysis", "Manual diagnostic reanalysis by laboratory experts",
             "Expert re-interpretation of a case in a diagnostic laboratory using a tertiary interpretation platform and current literature.",
             {"reported_name": "Manual reanalysis", "entity_level": "method", "source_locator": "Methods 'Manual Reanalysis of Previously No-Finding and Cases with VUS Findings' P1-P3",
              "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; the workflow is on the configuration"}}},
             [S], facets=dict(FAC, method_types=["conventional_pipeline"]))


def config(short, name, of, version, params, locator, mtype="conventional_pipeline", reported=None, limitations=None):
    a = {"reported_name": reported or name, "foundation_model_eligible": False, "version": version, "parameters": params, "source_locator": locator}
    if limitations:
        a["limitations"] = limitations
    return rec("configuration", f"{P}-config-{short}", name, f"{name} as run in Kaschta et al. 2026.", a, [S],
               links=[("configuration_of", of)], facets=dict(FAC, method_types=[mtype]))


C_MAN = config("manual-emedgene-dragen-4-2-4", "Manual reanalysis in Illumina Emedgene with DRAGEN v4.2.4 re-calling (Kaschta et al. 2026)", MANUAL,
               "DRAGEN germline v4.2.4 (small variants), v4.2 (SMN copy number, STR and SV calling); Emedgene version not printed",
               "Raw FASTQ re-aligned and re-called; updated annotation, allele frequencies, curated clinical information and current literature; mean time recorded per case",
               "Methods 'Manual Reanalysis of Previously No-Finding and Cases with VUS Findings' P1-P3; Results 'Cohort' P2", reported="Manual reanalysis (Illumina Emedgene)")
C_TAL = config("talos-8-2-0-archived-dragen-vcf", "Talos 8.2.0 on archived DRAGEN v3.7.5 VCFs, pedigree where available (Kaschta et al. 2026)", TALOS, "8.2.0",
               "Workflow customised to accept VCFs already annotated by DRAGEN; archived per-case VCFs, pedigree information where available and optional HPO terms; no manual curation; trio mode applies inheritance filtering",
               "Methods 'Study Cohort and Reanalysis Design' P3; 'Automated Reanalysis Using Talos' P1-P4", reported="Talos",
               limitations=["Adapted by the authors to ingest DRAGEN-annotated VCFs; conversion errors stopped some variants entering prioritisation (Results)."])
C_TAL_PO = config("talos-8-2-0-proband-only", "Talos 8.2.0, proband-only mode on trio cases (Kaschta et al. 2026)", TALOS, "8.2.0",
                  "As the archived-VCF configuration, run without parental genotypes", "Results 'Benchmarking of Automated Reanalysis: Trio Cases' P3", reported="Talos (proband-only mode)")

# ---------------------------------------------------------------- datasets and protocols
D_RE = rec("dataset", f"{P}-data-uksh-219-unresolved-genomes", "UKSH rare-disease genomes without a prior P/LP finding: 219 cases (Kaschta et al. 2026)",
           "Index cases from routine genome sequencing at University Medical Center Schleswig-Holstein that had no P/LP finding at the initial analysis.",
           {"version": "As published (v1)", "patient_count": 219,
            "population": "49 cases with VUS findings and 170 cases with no findings, within a 377-case cohort (305 trios or multi-member families, 72 singletons) sequenced January 2022 to April 2023; mean interval to reanalysis 660 days (range 208 to 1,208)",
            "assay": "PCR-free short-read genome sequencing, Illumina NovaSeq, GRCh38; mean coverage 38x", "split": "No split",
            "reuse_restrictions": "Per-patient data are in a supplement that was not retrieved; study-level aggregates only",
            "source_locator": "Methods 'Study Cohort and Reanalysis Design' P2-P3; Results 'Cohort' P1-P2"}, [S], facets=FAC)
D_BS = rec("dataset", f"{P}-data-uksh-singleton-benchmark", "UKSH singleton benchmarking cases with known findings (Kaschta et al. 2026)",
           "Singleton cases with an initial P/LP or VUS finding, used as positive controls for Talos.",
           {"version": "As published (v1)", "patient_count": 45, "population": "29 cases with 35 P/LP variants and 16 cases with 21 VUS", "split": "No split",
            "source_locator": "Results 'Benchmarking of Automated Reanalysis: Singleton Cases' P1"}, [S], facets=FAC)
D_BT = rec("dataset", f"{P}-data-uksh-trio-benchmark", "UKSH trio benchmarking cases with known findings (Kaschta et al. 2026)",
           "Trio cases with an initial P/LP or VUS finding, used as positive controls for Talos.",
           {"version": "As published (v1)", "patient_count": 162, "population": "129 cases with 145 P/LP variants and 33 cases with 43 VUS", "split": "No split",
            "source_locator": "Results 'Benchmarking of Automated Reanalysis: Trio Cases' P1"}, [S], facets=FAC)

RE_LIM = [
    "Unequal inputs: the manual arm re-aligned and re-called the raw reads with DRAGEN v4.2.4 and used Emedgene; Talos used the archived DRAGEN v3.7.5 VCFs. Differences cannot be attributed to the method alone.",
    "The reference is the manual arm's own result: Talos is scored on whether it returned what manual reanalysis found, so findings that only Talos might have made are not counted.",
    "Very small numbers: three new P/LP cases in each arm.",
    "Automated total diagnostic yield is printed as 41.9% (Results 'Reanalysis Diagnostic Yield: Automated Reanalysis' P1), but 161 of 377 is 42.7%, which the manual paragraph and Figure 4 legend print; 41.9% is the initial yield.",
    "Talos output per case is printed as an average of three variants (Results; Discussion P3) and as a median of approximately three (Discussion P1).",
    "Manual time excludes report writing and preparation of evidence for secondary review; no hands-on time is printed for Talos.",
    "Single centre, high initial yield (41.9%), one reanalysis round after a mean of 660 days.",
    "A new candidate or classification is not a confirmed diagnosis; per-case confirmation details are in the supplement, which was not read."]
P_RE = rec("protocol", f"{P}-protocol-manual-vs-talos-219-reanalysis", "Manual versus Talos reanalysis of 219 unresolved genomes after a mean 660 days (Kaschta et al. 2026)",
           "New P/LP and VUS findings, case-category counts and review effort from manual and automated reanalysis of the same unresolved cases.",
           {"protocol": "Manual reanalysis of all 219 cases without a prior P/LP finding (October 2024 to December 2025); Talos applied to the whole cohort (October 2025); concordance defined as Talos returning the variants found or reclassified by manual reanalysis; outcomes counted at case level in the 377-case cohort.",
            "version": "medRxiv v1", "source_locator": "Methods 'Study Cohort and Reanalysis Design', 'Manual Reanalysis', 'Automated Reanalysis Using Talos', 'Concordance Analysis and Error Types'; Results 'Reanalysis Diagnostic Yield'",
            "limitations": RE_LIM}, [S], links=[("uses_data", D_RE)], facets=FAC)
BM_LIM = ["Positive controls are known findings from the initial analysis; recovering them does not establish new diagnostic yield.",
          "Concordance is per variant against the initial report, not per case.",
          "The pipeline conversion share for singletons is 8.6% in the text but 9.6% in the Figure 2 legend; the text value is stored (3 of 35 is 8.6%)."]
P_BS = rec("protocol", f"{P}-protocol-talos-singleton-benchmark", "Talos recovery of known P/LP and VUS variants in 45 singleton cases (Kaschta et al. 2026)",
           "Proportion of initially reported variants that Talos prioritised, with failure modes for missed P/LP variants.",
           {"protocol": "Track each reported variant in the benchmarking set; concordance is the share of known P/LP variants prioritised by Talos; misses grouped into error categories.",
            "version": "medRxiv v1", "source_locator": "Methods 'Benchmarking of Automated Reanalysis'; Results 'Benchmarking of Automated Reanalysis: Singleton Cases' P1-P3",
            "limitations": BM_LIM}, [S], links=[("uses_data", D_BS)], facets=FAC)
P_BT = rec("protocol", f"{P}-protocol-talos-trio-benchmark", "Talos recovery of known P/LP and VUS variants in 162 trio cases (Kaschta et al. 2026)",
           "Proportion of initially reported variants that Talos prioritised in trio mode and proband-only mode, with failure modes.",
           {"protocol": "As for singletons; trio cases run with parental genotypes, and again in proband-only mode.",
            "version": "medRxiv v1", "source_locator": "Methods 'Benchmarking of Automated Reanalysis'; Results 'Benchmarking of Automated Reanalysis: Trio Cases' P1-P3",
            "limitations": BM_LIM[:2] + ["Strict inheritance filtering in trio mode excluded 11 P/LP variants that proband-only mode recovered."]}, [S], links=[("uses_data", D_BT)], facets=FAC)

# ---------------------------------------------------------------- evaluations
def evaluation(short, name, cfg, proto, data, origin, comparison, locator, limitations=None):
    a = {"origin": origin, "protocol": proto, "version": "Primary source as retrieved 2026-10-10", "comparison": dict(comparison, protocol_id=proto), "source_locator": locator}
    if limitations:
        a["limitations"] = limitations
    return rec("evaluation", f"{P}-eval-{short}", name, "Published comparison; transcribed, not reproduced.", a, [S],
               links=[("system", cfg), ("assessment", proto), ("data", data)], facets=FAC)


RE_COMP = {"dataset_version": "UKSH cohort as published", "split": "No split", "population": "219 cases without a prior P/LP finding, counted within the 377-case cohort",
           "metric_implementation": "Case-level counts by the authors", "aggregation": "Cohort totals", "budget": None}
E_MAN = evaluation("manual-219-reanalysis", "Manual reanalysis of 219 unresolved genomes", C_MAN, P_RE, D_RE, "author_reported",
                   dict(RE_COMP, inputs="Raw reads re-called with DRAGEN v4.2.4; updated phenotype and literature", adaptation="Expert interpretation"),
                   "Results 'Reanalysis Diagnostic Yield: Manual Reanalysis' P1-P3", limitations=["The manual workflow is the authors' own diagnostic practice and is also the reference."])
E_TAL = evaluation("talos-219-reanalysis", "Talos reanalysis of 219 unresolved genomes", C_TAL, P_RE, D_RE, "independent_paper",
                   dict(RE_COMP, inputs="Archived DRAGEN v3.7.5 VCFs; pedigree where available; optional HPO terms", adaptation="No manual curation"),
                   "Results 'Reanalysis Diagnostic Yield: Automated Reanalysis' P1")
BM_COMP = {"dataset_version": "UKSH cohort as published", "split": "No split", "metric_implementation": "Per-variant tracking against the initial report",
           "aggregation": "Pooled over variants", "budget": None, "adaptation": "No manual curation"}
E_BS = evaluation("talos-singleton-benchmark", "Talos on 45 singleton benchmarking cases", C_TAL, P_BS, D_BS, "independent_paper",
                  dict(BM_COMP, population="35 P/LP and 21 VUS variants in 45 singleton cases", inputs="Archived DRAGEN v3.7.5 VCFs, singleton"),
                  "Results 'Benchmarking of Automated Reanalysis: Singleton Cases' P2-P3")
E_BT = evaluation("talos-trio-benchmark", "Talos in trio mode on 162 trio benchmarking cases", C_TAL, P_BT, D_BT, "independent_paper",
                  dict(BM_COMP, population="145 P/LP and 43 VUS variants in 162 trio cases", inputs="Archived DRAGEN v3.7.5 VCFs with parental genotypes"),
                  "Results 'Benchmarking of Automated Reanalysis: Trio Cases' P1-P2")
E_BTP = evaluation("talos-trio-benchmark-proband-only", "Talos in proband-only mode on 162 trio benchmarking cases", C_TAL_PO, P_BT, D_BT, "independent_paper",
                   dict(BM_COMP, population="145 P/LP variants in 162 trio cases", inputs="Archived DRAGEN v3.7.5 VCFs, proband only"),
                   "Results 'Benchmarking of Automated Reanalysis: Trio Cases' P3")

# ---------------------------------------------------------------- results from prose
HOW = ("Deterministic check of the pinned JATS XML (extract/extract_kaschta.py): the quoted phrase is asserted to occur in the named paragraph and the printed value in the phrase. "
       "Paragraph numbers count <p> elements directly inside each section.")
SEC = {"abs": "Abstract", "man": "Results > Reanalysis Diagnostic Yield: Manual Reanalysis", "aut": "Results > Reanalysis Diagnostic Yield: Automated Reanalysis",
       "sgl": "Results > Benchmarking of Automated Reanalysis: Singleton Cases", "tri": "Results > Benchmarking of Automated Reanalysis: Trio Cases"}


def result(short, ev, metric, direction, unit, printed, numeric, qualifier, sec, n, phrase, unit_detail=None, numerator=None, denominator=None, note=None):
    para = PARAS[(SEC[sec], n)]
    assert phrase in para, (short, phrase)
    assert printed in phrase, (short, printed)
    if numeric is not None:
        float(numeric)
    loc = f"{SEC[sec].replace(' > ', ', ')} P{n}, '{phrase}'"
    a = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed, "numeric_value": numeric, "source_locator": loc,
         "metric_qualifier": qualifier, "missing_metadata": {"uncertainty": {"reason": "unreported"}},
         "review": {"method": ["transcription"], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
                    "date": DATE, "artifact_sha256": SHA, "retrieval_url": JATS_URL, "note": HOW + (" " + note if note else "") + " Pending independent review."}}
    for k, v in (("unit_detail", unit_detail), ("numerator", numerator), ("denominator", denominator)):
        if v is not None:
            a[k] = v
    rid = f"{P}-result-{short}"
    rec("result", rid, f"{short} {metric}", "Reported measurement transcribed from the pinned source text. Not independently reproduced.", a, [S], links=[("evaluation", ev)])
    claims_rows.append([rid, S, loc, printed, "result"])


# Manual arm
result("manual-new-plp-cases", E_MAN, "count", "higher", "count", "three", "3", "cases with a new P/LP finding", "abs", 3, "Manual reanalysis identified three additional P/LP cases", unit_detail="cases")
result("manual-new-vus-cases", E_MAN, "count", "unknown", "count", "two", "2", "cases newly classified as VUS findings", "abs", 3, "two newly classified as VUS", unit_detail="cases")
result("manual-cases-with-new-findings", E_MAN, "count", "higher", "count", "five", "5", "cases with newly reported findings (P/LP or VUS)", "man", 1, "identified five cases with newly reported findings", unit_detail="cases")
result("manual-plp-cases-after", E_MAN, "count", "higher", "count", "161", "161", "cohort cases with a reported P/LP finding after reanalysis (158 before)", "man", 3, "increased the number of cases with a reported P/LP finding from 158 to 161", unit_detail="cases of 377")
result("manual-total-diagnostic-yield", E_MAN, "diagnostic-yield", "higher", "percent", "42.7%", "42.7", "total P/LP diagnostic rate in the 377-case cohort after reanalysis", "man", 3, "yielding a total diagnostic rate of 42.7%")
result("manual-vus-cases-after", E_MAN, "count", "unknown", "count", "50", "50", "cohort cases with VUS findings after reanalysis (49 before)", "man", 3, "The number of cases with VUS findings increased from 49 to 50", unit_detail="cases")
result("manual-no-finding-cases-after", E_MAN, "count", "lower", "count", "166", "166", "cohort cases without a reported clinically relevant finding after reanalysis (170 before)", "man", 3, "decreased from 170 to 166", unit_detail="cases")
result("manual-review-time", E_MAN, "review-time-per-case", "lower", "minute", "81 minutes", "81", "mean hands-on time for full manual case reanalysis, excluding report writing and secondary-review preparation", "man", 3, "The mean reanalysis time was 81 minutes per case")
# Talos arm
result("talos-new-plp-cases", E_TAL, "count", "higher", "count", "three", "3", "cases with a new P/LP finding", "aut", 1, "also identified the three new P/LP cases", unit_detail="cases")
result("talos-new-vus-cases-recovered", E_TAL, "count", "higher", "count", "one", "1", "of the two cases newly classified as VUS by manual reanalysis, cases also prioritised", "abs", 3, "only identified one of the two new VUS findings", unit_detail="cases", denominator=2)
result("talos-plp-cases-after", E_TAL, "count", "higher", "count", "161", "161", "cohort cases with a reported P/LP finding after reanalysis (158 before)", "aut", 1, "increased the number of cases with a P/LP finding from 158 to 161", unit_detail="cases of 377")
result("talos-total-diagnostic-yield", E_TAL, "diagnostic-yield", "higher", "percent", "41.9%", "41.9", "total P/LP diagnostic rate in the 377-case cohort after reanalysis, as printed", "aut", 1, "41.9% total diagnostic yield",
       note="Printed 41.9% equals the initial 158 of 377; the same paragraph prints 158 to 161, which is 42.7%. Kept as printed.")
result("talos-vus-cases-after", E_TAL, "count", "unknown", "count", "49", "49", "cohort cases with VUS findings after reanalysis (49 before)", "aut", 1, "The number of cases based on results with VUS findings remained at 49", unit_detail="cases")
result("talos-no-finding-cases-after", E_TAL, "count", "lower", "count", "167", "167", "cohort cases without a prioritised finding after reanalysis (170 before)", "aut", 1, "decreased from 170 to 167", unit_detail="cases")
result("talos-candidates-per-case", E_TAL, "candidates-per-case", "lower", "variants-per-proband", "three", "3", "average variants returned per case, singleton and trio cases", "aut", 1, "On average, Talos returned three variants per case", unit_detail="variants per case")
# Benchmarking
result("singleton-plp-concordance", E_BS, "recall", "higher", "percent", "80.0%", "80.0", "known P/LP variants prioritised", "sgl", 2, "Talos prioritized 28 out of 35 P/LP variants (80.0% concordance)", numerator=28, denominator=35)
result("singleton-vus-captured", E_BS, "count", "unknown", "count", "two", "2", "known VUS prioritised", "sgl", 2, "only two out of 21 VUS were captured", unit_detail="variants", denominator=21)
result("singleton-miss-hpo-gap", E_BS, "proportion", "lower", "percent", "11.4%", "11.4", "known P/LP variants missed because of HPO annotation gaps", "sgl", 3, "HPO annotation gaps (11.4%)")
result("singleton-miss-conversion", E_BS, "proportion", "lower", "percent", "8.6%", "8.6", "known P/LP variants missed because of pipeline conversion errors", "sgl", 3, "pipeline conversion errors (8.6%)",
       note="The Figure 2 legend prints 9.6% for the same category; the text value is stored.")
result("trio-plp-concordance", E_BT, "recall", "higher", "percent", "75.2%", "75.2", "known P/LP variants prioritised, trio mode", "tri", 1, "overall P/LP concordance of 75.2%", numerator=109, denominator=145)
result("trio-vus-captured", E_BT, "count", "unknown", "count", "Six", "6", "known VUS prioritised, trio mode", "tri", 1, "Six VUS variants were captured", unit_detail="variants", denominator=43)
for short, phrase, printed, q in (("out-of-scope", "four out-of-scope variant classes (2.8%)", "2.8%", "out-of-scope variant classes"),
                                  ("large-cnv", "three large copy-number variants not processed by the pipeline (2.1%)", "2.1%", "large copy-number variants not processed"),
                                  ("conversion", "nine pipeline conversion errors (6.2%)", "6.2%", "pipeline conversion errors"),
                                  ("hpo-gap", "nine HPO annotation gaps (6.2%)", "6.2%", "HPO annotation gaps")):
    result(f"trio-miss-{short}", E_BT, "proportion", "lower", "percent", printed, printed.rstrip("%"), f"known P/LP variants missed: {q}", "tri", 1, phrase)
result("trio-miss-inheritance-filter", E_BT, "proportion", "lower", "percent", "7.6%", "7.6", "known P/LP variants not prioritised because of trio inheritance filtering", "tri", 2, "An additional 11 P/LP variants (7.6%) were not prioritized")
result("trio-plp-concordance-proband-only", E_BTP, "recall", "higher", "percent", "82.8%", "82.8", "known P/LP variants prioritised, proband-only mode", "tri", 3, "increasing concordance to 82.8%")

# ---------------------------------------------------------------- claims
def claim(short, subject, field, value, locator):
    cid = f"{P}-claim-{short}"
    rec("claim", cid, f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.",
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "reviewer": ["claude"], "reviewer_note": "Claude (Opus 5.5) extraction agent; not an independent review",
                    "date": DATE, "artifact_sha256": SHA, "retrieval_url": JATS_URL, "note": "Hand transcription from the article text. Pending independent review."}},
        [S], links=[("subject", subject)])
    claims_rows.append([cid, S, locator, value, "claim"])


claim("unequal-inputs", P_RE, "input_difference",
      "Manual reanalysis re-aligned and re-called the original FASTQ files with DRAGEN v4.2.4 (v4.2 for SMN, STR and SV calling); Talos used archived per-case VCFs from the initial DRAGEN v3.7.5 analysis, with a workflow customised to accept DRAGEN-annotated VCFs without recalling variants.",
      "Methods 'Genome Sequencing, Primary Processing, and Quality Control' P1; 'Manual Reanalysis of Previously No-Finding and Cases with VUS Findings' P1; 'Automated Reanalysis Using Talos' P2-P3")
claim("drivers-of-new-findings", P_RE, "reported_finding",
      "All newly identified P/LP findings and clinically relevant VUS arose from updated variant-calling and interpretation pipelines, revised gene-disease validity evidence, newly published literature or GeneMatcher collaborations; none from correcting interpretive errors.",
      "Discussion 'Diagnostic Yield in the Context of Published Reanalysis Studies' P1")

# ---------------------------------------------------------------- judgements
CONSTR = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
          "Do not combine this mapping's evaluations with any other protocol's results, including the Talos 2026 study mappings."]
J = []


def judgement(short, proto, relevance, endpoint, rationale, limitations, group, title, headline, stratum=None, order=None, cites=None):
    cites = cites or [(S, "See data/omics/use-case-coverage-reanalysis-kaschta-20261010/claims.csv")]
    a = {"field": f"links:assessed_by:{proto}", "value": proto, "relevance": relevance, "endpoint": endpoint, "rationale": rationale, "constraints": CONSTR,
         "limitations": limitations, "citation_locators": [{"source_id": s, "locator": l} for s, l in cites],
         "source_locator": "; ".join(f"{s}: {l}" for s, l in cites), "revision": 1,
         "reason": "Recorded from the Kaschta et al. follow-up pass 2026-10-10 (data/omics/use-case-coverage-reanalysis-kaschta-20261010/).",
         "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        a["stratum_label"], a["stratum_order"] = stratum, order
    pname = next(r["name"] for r in records if r["id"] == proto)
    rec("claim", f"use-case-mapping-reanalysis-kaschta-20261010-{short}", f'Relevance of {pname} to "{UC_NAME}"', rationale, a, [S], links=[("subject", UC)])
    J.append(proto)


judgement("manual-vs-talos", P_RE, "direct",
          "New P/LP and VUS case findings, case-category counts, manual review time and Talos candidates per case for manual and Talos reanalysis of the same 219 unresolved genomes",
          "Manual and automated reanalysis of the same unresolved cohort after the same interval, with new-finding counts and review effort for both arms, directly answers which method finds new diagnoses or reduces review effort. "
          "The arms did not receive the same variant calls (the manual arm re-called with a newer DRAGEN), which favours the manual arm; any difference, and the matching three P/LP gains, must be read with that in mind.",
          RE_LIM, "kaschta2026-reanalysis", "Manual versus Talos reanalysis on one cohort (Kaschta et al. 2026)", "count", "Reanalysis of 219 unresolved cases", 1,
          cites=[(S, "Results 'Reanalysis Diagnostic Yield: Manual Reanalysis' P1-P3 and 'Automated Reanalysis' P1; Abstract P3; Methods")])
judgement("talos-singleton-benchmark", P_BS, "proxy",
          "Share of 35 known P/LP variants and count of 21 known VUS that Talos prioritised in 45 singleton cases, with failure modes",
          "Recovering known findings checks that the automated pipeline would not miss established diagnoses, which bears on trusting it for reanalysis, but reranking known solved cases does not establish new diagnostic yield.",
          BM_LIM, "kaschta2026-reanalysis", "Manual versus Talos reanalysis on one cohort (Kaschta et al. 2026)", "recall", "Talos benchmark, singletons", 2,
          cites=[(S, "Results 'Benchmarking of Automated Reanalysis: Singleton Cases' P1-P3")])
judgement("talos-trio-benchmark", P_BT, "proxy",
          "Share of 145 known P/LP variants Talos prioritised in 162 trio cases in trio mode and proband-only mode, VUS captured and failure modes",
          "As for the singleton benchmark: known-finding recovery, not new yield. It shows the effect of trio inheritance filtering.",
          BM_LIM[:2] + ["Strict inheritance filtering in trio mode excluded 11 P/LP variants that proband-only mode recovered."],
          "kaschta2026-reanalysis", "Manual versus Talos reanalysis on one cohort (Kaschta et al. 2026)", "recall", "Talos benchmark, trios", 3,
          cites=[(S, "Results 'Benchmarking of Automated Reanalysis: Trio Cases' P1-P3")])

records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
assert len(ids) == len(set(ids))
with open(os.path.join(OUT, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
claims_rows.sort()
with open(os.path.join(OUT, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True))
print("judged protocols:", J)
