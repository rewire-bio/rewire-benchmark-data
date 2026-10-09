"""Deterministic extraction of rare-disease reanalysis method comparisons into a records batch.

Usage: python3 -I extract_rare_reanalysis.py <download-dir> <batch-dir>

Reads the pinned article XML (standard library) and the two supplementary PDFs through
`pdftotext -layout` (poppler; the version is recorded in retrieval-log.md), asserts every
row and column label it relies on, and writes batch.jsonl (store form), claims.csv and
extract/judgements.json. printed_value is the cell text exactly as printed.

It also writes relevance judgements for seven protocols already in the store (the Talos
Table 1 strata and the Exomiser comparison from the same study); those protocols, their
evaluations and results are not modified.
"""
import csv, hashlib, json, re, subprocess, sys
import xml.etree.ElementTree as ET
from collections import Counter
from decimal import Decimal

DL, BATCH = sys.argv[1], sys.argv[2]
P = "rare-reanalysis-20261009"
UC = "use-case-unresolved-rare-disease-reanalysis"
UC_NAME = "Reanalyse unresolved rare-disease cases"
DATE = "2026-10-09"
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
PDF_NOTE = ("Extracted by deterministic parse of `pdftotext -layout` output of the pinned supplementary PDF "
            "(extract/extract_rare_reanalysis.py), with row and column labels asserted. printed_value is the token as "
            "printed. Pending independent review.")
XML_NOTE = ("Extracted by deterministic parse of the pinned Europe PMC full-text XML (extract/extract_rare_reanalysis.py), "
            "with row and column labels asserted. printed_value is the cell text as printed. Pending independent review.")
PATHS = {
    "dem_xml": f"{DL}/dl-PMC11513043/article.xml",
    "dem_pdf": f"{DL}/dl-PMC11513043-supp/x/41525_2024_436_MOESM1_ESM.pdf",
    "ves_xml": f"{DL}/dl-PMC11655964/article.xml",
    "ves_pdf": f"{DL}/dl-PMC11655964-supp/x/41525_2024_456_MOESM1_ESM.pdf",
}
records, claims_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def need(got, expected, where):
    if got != expected:
        raise SystemExit(f"Label check failed at {where}: expected {expected!r}, got {got!r}")


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids, "links": links or [],
         "attributes": attributes or {}}
    records.append(r)
    return r


def review(note, method=("deterministic-table-parse",)):
    return {"method": list(method), "reviewer": ["claude"],
            "reviewer_note": "Claude (Opus 5.5) research agent, the extractor; no independent or human review claimed",
            "date": DATE, "note": note}


def result(id_, eval_id, source_id, locator, printed, numeric, metric, direction, unit, qualifier=None, unit_detail=None,
           extra=None, note=PDF_NOTE):
    attrs = {"metric": metric, "metric_direction": direction, "unit": unit, "printed_value": printed, "numeric_value": numeric,
             "source_locator": locator, "missing_metadata": {"uncertainty": {"reason": "unreported"}}}
    if qualifier:
        attrs["metric_qualifier"] = qualifier
    if unit_detail:
        attrs["unit_detail"] = unit_detail
    if extra:
        attrs.update(extra)
    attrs["review"] = review(note)
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric}" + (f" ({qualifier})" if qualifier else ""),
        "Reported measurement transcribed from the pinned source. Not independently reproduced.", [source_id],
        [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claims_rows.append([id_, source_id, locator, printed, "result"])


def claim(id_, subject, field, value, source_id, locator):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", [source_id],
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": review("Transcribed from the pinned source. Pending independent review.", ("transcription",))}, facets={})
    claims_rows.append([id_, source_id, locator, value, "claim"])


def evaluation(id_, name, system, protocol, dataset, source_ids, origin, comparison, locator, extra=None):
    attrs = {"origin": origin, "protocol": protocol, "version": f"Primary source as retrieved {DATE}",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    attrs.update(extra or {})
    rec(id_, "evaluation", name, "Published reanalysis method comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": system}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs)


def configuration(id_, name, description, of, source_ids, reported_name, locator, version, parameters, version_note=None):
    attrs = {"reported_name": reported_name, "source_locator": locator, "foundation_model_eligible": False,
             "parameters": parameters}
    if version:
        attrs["version"] = version
    else:
        attrs["missing_metadata"] = {"version": version_note}
    rec(id_, "configuration", name, description, source_ids, [{"relation": "configuration_of", "target_id": of}], attrs,
        facets={**FACETS, "method_types": ["conventional_pipeline"]})


def method(key, name, description, source_id, locator):
    id_ = f"{P}-method-{key}"
    rec(id_, "method", name, description, [source_id], [],
        {"reported_name": name, "entity_level": "method", "source_locator": locator,
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}},
        facets={**FACETS, "method_types": ["conventional_pipeline"]})
    return id_


def source(id_, name, doi, artifact_url, path, version, retrieved, licence, venue, year, locator, media_type, extra=None):
    attrs = {"url": f"https://doi.org/{doi}", "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved,
             "artifact_sha256": sha(path), "doi": doi, "publication_status": "peer_reviewed", "licence": licence,
             "media_type": media_type, "venue": venue, "year": year, "source_locator": locator}
    attrs.update(extra or {})
    rec(id_, "source", name, "Primary source retrieved and hashed for the rare-disease reanalysis use-case pass.", [], [], attrs)


def pdf_lines(path):
    out = subprocess.run(["pdftotext", "-layout", path, "-"], check=True, capture_output=True).stdout.decode("utf-8")
    return out.split("\n")


def txt(e):
    return " ".join("".join(e.itertext()).split())


def table_grid(xml_path, table_id):
    root = ET.parse(xml_path).getroot()
    tw = next(t for t in root.iter("table-wrap") if t.get("id") == table_id)
    grid, pending = [], {}
    for tr in tw.iter("tr"):
        row, col, ci = [], 0, 0
        cells = [c for c in tr if c.tag in ("td", "th")]
        while ci < len(cells) or col in pending:
            if col in pending:
                text, left = pending[col]
                row.append(text)
                if left - 1:
                    pending[col] = (text, left - 1)
                else:
                    del pending[col]
                col += 1
                continue
            c = cells[ci]; ci += 1
            cs, rs = int(c.get("colspan") or 1), int(c.get("rowspan") or 1)
            for _ in range(cs):
                row.append(txt(c))
                if rs > 1:
                    pending[col] = (txt(c), rs - 1)
                col += 1
        grid.append(row)
    return grid, txt(tw.find("caption")), txt(tw.find("table-wrap-foot")) if tw.find("table-wrap-foot") is not None else ""


# ================================================================= sources
S_DEM, S_DEM_SUPP = f"{P}-source-demidov2024", f"{P}-source-demidov2024-supp"
S_VES, S_VES_SUPP = f"{P}-source-vestito2024", f"{P}-source-vestito2024-supp"
source(S_DEM, "Comprehensive reanalysis for CNVs in ES data from unsolved rare disease cases results in new diagnoses",
       "10.1038/s41525-024-00436-6", f"{EPMC}/PMC11513043/fullTextXML", PATHS["dem_xml"],
       "npj Genomic Medicine 9:49, published online 2024-10-26; PMC11513043 full-text XML", "2026-10-09T20:40:13Z", "CC-BY-4.0",
       "npj Genomic Medicine", 2024, "Licence statement in the article XML <license> element: Creative Commons Attribution 4.0", "application/xml")
source(S_DEM_SUPP, "Demidov et al. 2024, Supplementary Information (Supplementary Tables 1-5)", "10.1038/s41525-024-00436-6",
       f"{EPMC}/PMC11513043/supplementaryFiles", PATHS["dem_pdf"],
       "41525_2024_436_MOESM1_ESM.pdf from the Europe PMC supplementary bundle (hash is of the PDF; the bundle zip is rebuilt per request)",
       "2026-10-09T20:40:40Z", "CC-BY-4.0", "npj Genomic Medicine", 2024,
       "Article licence (Creative Commons Attribution 4.0) covers its supplementary information", "application/pdf")
source(S_VES, "Efficient reinterpretation of rare disease cases using Exomiser", "10.1038/s41525-024-00456-2",
       f"{EPMC}/PMC11655964/fullTextXML", PATHS["ves_xml"],
       "npj Genomic Medicine 9:65, published 2024-12-18; PMC11655964 full-text XML", "2026-10-09T20:36:38Z", "CC-BY-NC-ND-4.0",
       "npj Genomic Medicine", 2024, "Licence statement in the article XML <license> element: Creative Commons Attribution-NonCommercial-NoDerivatives 4.0",
       "application/xml")
source(S_VES_SUPP, "Vestito et al. 2024, Supplementary Table 1", "10.1038/s41525-024-00456-2", f"{EPMC}/PMC11655964/supplementaryFiles",
       PATHS["ves_pdf"], "41525_2024_456_MOESM1_ESM.pdf from the Europe PMC supplementary bundle (PDF title 'Supplementary_table_S1 copy', 4 pages)",
       "2026-10-09T20:36:47Z", "CC-BY-NC-ND-4.0", "npj Genomic Medicine", 2024,
       "Article licence (CC BY-NC-ND 4.0) covers its supplementary information", "application/pdf",
       {"limitations": ["The PDF has a header row but no title or legend; the database releases compared are not printed in it (see claim on the protocol)."]})

# ================================================================= Demidov et al. 2024 (Solve-RD CNV reanalysis)
g1, cap1, foot1 = table_grid(PATHS["dem_xml"], "Tab1")
need(cap1, "Table showing overall number of CNV calls submitted for clinical interpretation following filtering, separated by type and caller used", "Demidov Table 1 caption")
need(foot1, "Numbers in brackets denote the subset of calls detected on sex chromosomes.", "Demidov Table 1 footnote")
need(g1[1], ["Tool", "Long", "0", "1", "2", "3", "4", ">4", "Total"], "Demidov Table 1 header")
need([r[0] for r in g1[2:]], ["ClinCNV", "Conifer", "ExomeDepth", "Total", "% of Events"], "Demidov Table 1 rows")
lines = pdf_lines(PATHS["dem_pdf"])
i4 = [l.strip() for l in lines].index("Supplementary Table 4")
hdr = [l for l in lines[i4 + 1:i4 + 6] if l.strip()]
need(re.sub(r"\s+", " ", hdr[0]).strip(), "Tool Deletions Duplications All CNVs Proportion of Proportion of", "Demidov Supp Table 4 header line 1")
s4 = {}
for l in lines[i4 + 1:i4 + 14]:
    m = re.fullmatch(r"\s*(ClinCNV|Conifer|ExomeDepth|Total)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*", l)
    if m:
        s4[m.group(1)] = m.groups()[1:]
need(sorted(s4), ["ClinCNV", "Conifer", "ExomeDepth", "Total"], "Demidov Supp Table 4 rows")
need(any("Supplementary Table 4. Summary statistics regarding 7,849 CNVs initially returned for" in l for l in lines), True, "Demidov Supp Table 4 legend")


def dem_num(printed, where):
    """Supplementary Table 4 prints '.' as thousands separator and ',' as decimal separator."""
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", printed):
        return printed.replace(".", "")
    if re.fullmatch(r"\d+,\d+", printed):
        return printed.replace(",", ".")
    if re.fullmatch(r"\d+", printed):
        return printed
    raise SystemExit(f"Unparsed number {printed!r} at {where}")


def t1_split(cell, where):
    m = re.fullmatch(r"([\d,]+) \((\d+)\)", cell)
    if not m:
        raise SystemExit(f"Unparsed Table 1 cell {cell!r} at {where}")
    return m.group(1).replace(",", ""), m.group(2)


DM = {"ClinCNV": method("clincnv", "ClinCNV", "Read-depth CNV caller for exome data using tiled target regions and sample clustering.", S_DEM, "Methods 'ClinCNV Workflow'"),
      "Conifer": method("conifer", "CoNIFER", "Read-depth CNV caller for exome data using singular value decomposition of RPKM values.", S_DEM, "Methods 'Conifer workflow'"),
      "ExomeDepth": method("exomedepth", "ExomeDepth", "Read-depth CNV caller for exome data using a beta-binomial model against a matched reference set.", S_DEM, "Methods 'ExomeDepth workflow'")}
DPARAM = {"ClinCNV": "Called in 28 batches by enrichment kit; calls with log likelihood of at least 20 taken forward (Methods 'Alignment and definition of capture regions of interest' paragraph 2), then ERN-specific filters",
          "Conifer": "Called in batches by enrichment kit; SVD-ZRPKM beyond +/-1.75 taken forward; batches rerun with more SVD components until the median call count was below 10 (Methods 'Conifer workflow'), then ERN-specific filters",
          "ExomeDepth": "Called in batches by enrichment kit with a correlated reference set per sample; samples with reference correlation below 0.97 failed QC. The Bayes factor threshold is printed as BF > 15 in Methods 'Alignment and definition of capture regions of interest' paragraph 2 and as discarding BF < 0.15 in 'ExomeDepth workflow' paragraph 2. Then ERN-specific filters"}
DC = {}
for tool in ["ClinCNV", "Conifer", "ExomeDepth"]:
    cid = f"{P}-config-demidov2024-{tool.lower()}"
    DC[tool] = cid
    configuration(cid, f"{tool} in the Solve-RD exome CNV reanalysis (Demidov et al. 2024)",
                  f"{tool} as applied to 9171 Solve-RD exomes in batches by enrichment kit.", DM[tool], [S_DEM], tool,
                  "Methods 'Alignment and definition of capture regions of interest' paragraph 2 and the caller workflow section", None, DPARAM[tool],
                  version_note={"reason": "unreported", "note": "No caller version is printed in the article text read"})
D_DATA = f"{P}-data-demidov2024-solverd-unsolved-exomes"
rec(D_DATA, "dataset", "Solve-RD unsolved rare-disease exomes reanalysed for CNVs (Demidov et al. 2024)",
    "Exome datasets that local analysis had not resolved, pooled across 42 research groups and four European Reference Networks.", [S_DEM, S_DEM_SUPP], [],
    {"version": "Solve-RD exome data as analysed in Demidov et al. 2024", "population": "9171 exome datasets from 5757 families (6143 affected individuals) affected by a rare disease, generated with 28 enrichment kits by 42 research groups; each group had already analysed its data without a diagnosis.",
     "split": "No split; analysed in 28 batches by enrichment kit", "denominator": 5757,
     "source_locator": "Abstract; Introduction paragraph 5; Supplementary Table 3"})
DP = f"{P}-protocol-demidov2024-cnv-calls-for-interpretation"
rec(DP, "protocol", "CNV calls returned to clinical experts per caller after filtering, Solve-RD exome reanalysis (Demidov et al. 2024 Table 1, Supplementary Table 4)",
    "Number of rare CNV calls each caller contributed for expert interpretation, by copy number and type, on the same unsolved cohort.", [S_DEM, S_DEM_SUPP],
    [{"relation": "uses_data", "target_id": D_DATA}],
    {"protocol": "Each caller's calls after tool-specific quality filters, removal of commonly observed events and restriction to genes on the relevant ERN gene list, counted as returned to the submitting clinical experts for interpretation. Long CNVs are counted separately from the copy-number classes; bracketed values are the sex-chromosome subset.",
     "version": "Table 1 and Supplementary Table 4", "denominator": 5757,
     "source_locator": "Results 'Technical results' paragraphs 2-3; Table 1; Supplementary Table 4",
     "limitations": ["Measures review workload per caller, not new diagnoses per caller; per-caller detection of the confirmed pathogenic CNVs is printed only in the Results text (claim on this protocol).",
                     "Calling and filtering thresholds differ between callers and ERNs, so counts reflect each caller as configured.",
                     "ClinCNV was developed by a Solve-RD partner (Methods)."],
     "missing_metadata": {"uncertainty": {"reason": "inapplicable", "note": "Counts from a single analysis"}}})
D_COMP = {"dataset_version": "Solve-RD exomes, 9171 datasets", "split": "No split", "population": "5757 unsolved families",
          "inputs": "Exome alignments re-processed centrally", "adaptation": "Caller-specific thresholds and ERN filters",
          "metric_implementation": "Count of calls returned for interpretation", "aggregation": "Whole cohort", "budget": None}
COLS = ["Long", "0", "1", "2", "3", "4", ">4", "Total"]
for ri, tool in enumerate(["ClinCNV", "Conifer", "ExomeDepth"]):
    row = g1[2 + ri]
    ev = f"{P}-eval-demidov2024-{tool.lower()}"
    origin = "author_reported" if tool == "ClinCNV" else "independent_paper"
    extra = {"limitations": ["ClinCNV was developed by a Solve-RD partner (Methods 'Alignment and definition of capture regions of interest' paragraph 2), so this row is recorded as author_reported."]} if tool == "ClinCNV" else None
    evaluation(ev, f"{tool}: CNV calls returned for interpretation (Solve-RD)", DC[tool], DP, D_DATA, [S_DEM, S_DEM_SUPP], origin, D_COMP,
               f"Table 1 row '{tool}'; Supplementary Table 4 row '{tool}'", extra=extra)
    for ci, col in enumerate(COLS):
        cell = row[ci + 1]
        tot, sex = t1_split(cell, f"Table 1 {tool} {col}")
        label = "long CNVs" if col == "Long" else ("all classes" if col == "Total" else f"copy number {col}")
        slug = {"Long": "long", "0": "cn0", "1": "cn1", "2": "cn2", "3": "cn3", "4": "cn4", ">4": "cn-gt4", "Total": "total"}[col]
        loc = f"Table 1, row '{tool}', column '{col}'"
        result(f"{P}-result-demidov2024-{tool.lower()}-{slug}", ev, S_DEM, loc + " (value outside brackets)", cell, tot, "count", "unknown", "count",
               qualifier=f"CNV calls returned for interpretation, {label}, all chromosomes", unit_detail="CNV calls", note=XML_NOTE,
               extra={"source_label": "value outside brackets"})
        result(f"{P}-result-demidov2024-{tool.lower()}-{slug}-sex-chromosomes", ev, S_DEM, loc + " (value in brackets)", cell, sex, "count", "unknown", "count",
               qualifier=f"CNV calls returned for interpretation, {label}, sex chromosomes", unit_detail="CNV calls", note=XML_NOTE,
               extra={"source_label": "value in brackets (sex-chromosome subset, table footnote)"})
    dels, dups, allc, prop_all, prop_dup = s4[tool]
    for printed, metric, qual, unit, slug, udet in [
            (dels, "count", "deletions returned for interpretation", "count", "s4-deletions", "CNV calls"),
            (dups, "count", "duplications returned for interpretation", "count", "s4-duplications", "CNV calls"),
            (allc, "count", "all CNVs returned for interpretation", "count", "s4-all", "CNV calls"),
            (prop_all, "proportion", "share of all CNV calls contributed by this caller", "fraction", "s4-share-of-all", None),
            (prop_dup, "proportion", "share of this caller's calls that are duplications", "fraction", "s4-share-duplications", None)]:
        result(f"{P}-result-demidov2024-{tool.lower()}-{slug}", ev, S_DEM_SUPP, f"Supplementary Table 4 (page with heading 'Supplementary Table 4'), row '{tool}', column '{qual}'",
               printed, dem_num(printed, f"Supp Table 4 {tool}"), metric, "unknown", unit, qualifier=qual, unit_detail=udet,
               extra={"numeric_representation": "Supplementary Table 4 prints '.' as a thousands separator and ',' as the decimal separator; the row totals match Table 1 (for example 2.782 here and 2,782 in Table 1)"})
    need(dem_num(allc, tool), tot, f"Supp Table 4 all CNVs equals Table 1 total for {tool}")
claim(f"{P}-claim-demidov2024-pooled-calls", DP, "pooled_call_counts",
      "Table 1 'Total' row: " + "; ".join(f"{c} {v}" for c, v in zip(COLS, g1[5][1:])) + ". '% of Events' row: " + "; ".join(f"{c} {v}" for c, v in zip(COLS, g1[6][1:])) +
      ". Supplementary Table 4 'Total' row: deletions " + s4["Total"][0] + ", duplications " + s4["Total"][1] + ", all " + s4["Total"][2] + ", proportions " + s4["Total"][3] + " and " + s4["Total"][4] + ".",
      S_DEM, "Table 1 rows 'Total' and '% of Events'; Supplementary Table 4 row 'Total'")
claim(f"{P}-claim-demidov2024-per-caller-detection", DP, "pathogenic_cnv_detection_by_caller",
      "Of 77 confirmed pathogenic CNVs, 40 were initially identified by all three callers (Conifer's call was later discarded for ten of them, and ExomeDepth's for one). Of the remaining 37, ClinCNV identified 36 (two later failed ClinCNV quality thresholds), ExomeDepth 25 (five later discarded for a low Bayes factor), and one duplication in PIEZO2 was identified by Conifer alone. A diagnosis was provided to 51 families.",
      S_DEM, "Results 'Diagnostic results' paragraph 2; Abstract")
claim(f"{P}-claim-demidov2024-workload", DP, "interpretation_workload",
      "7849 calls in 3436 affected individuals from 3300 families were returned for interpretation, a mean of 1.3 CNVs per proband or 2.4 per proband with at least one call; a further 393 CNV-SNV compound heterozygous pairs in 226 individuals were also returned.",
      S_DEM, "Results 'Technical results' paragraph 2")

# ================================================================= Vestito et al. 2024 (Exomiser reanalysis thresholds)
vl = pdf_lines(PATHS["ves_pdf"])
need(re.sub(r"\s+", " ", vl[0]).strip(), "Diff human score Var score TP FN FP TN recall precision Fscore F2score", "Vestito Supp Table 1 header")
rows = []
for n, l in enumerate(vl):
    if re.match(r"\s*0\.\d", l):
        tok = l.split()
        need(len(tok), 10, f"Vestito Supp Table 1 line {n + 1} token count")
        rows.append((n + 1, tok))
need(len(rows), 81, "Vestito Supp Table 1 row count")
GRID = [f"0.{i}" for i in range(1, 10)]
need(sorted((t[0], t[1]) for _, t in rows), sorted((a, b) for a in GRID for b in GRID), "Vestito Supp Table 1 threshold grid")
for _, t in rows:
    need(int(t[2]) + int(t[3]), 37, f"Vestito TP+FN for {t[0]},{t[1]}")
    need(int(t[2]) + int(t[3]) + int(t[4]) + int(t[5]), 1846, f"Vestito TP+FN+FP+TN for {t[0]},{t[1]}")
EXOMISER = "uc-clinical-20260930-method-exomiser"
V_DATA = f"{P}-data-vestito2024-100kgp-37-new-gene-cases"
rec(V_DATA, "dataset", "100,000 Genomes Project: 37 cases unsolved in February 2019 and later diagnosed through a new disease-gene association (Vestito et al. 2024)",
    "Cases whose diagnosis involved a disease-gene association added to OMIM between February 2019 and February 2022.", [S_VES, S_VES_SUPP], [],
    {"version": "100kGP primary pipeline cases as analysed in Vestito et al. 2024", "population": "37 solved 100kGP cases diagnosed in a disease-gene association that appeared in OMIM between February 2019 and February 2022; Supplementary Table 1 scores 1846 Exomiser candidate variants (37 diagnosed variants).",
     "split": "No split", "denominator": 37, "access": "Genomics England Research Environment under a collaborative agreement (Data availability)",
     "source_locator": "Results paragraph 5; Methods 'Reanalysis optimisation'; Supplementary Table 1 (TP + FN = 37, TP + FN + FP + TN = 1846 in every row)"})
VP = f"{P}-protocol-vestito2024-new-candidate-flagging"
rec(VP, "protocol", "Flagging new reanalysis candidates from Exomiser score changes across database releases (Vestito et al. 2024 Supplementary Table 1)",
    "Variant-level classification of Exomiser candidates flagged by a human phenotype score increase and a variant score threshold, against the later diagnoses.", [S_VES, S_VES_SUPP],
    [{"relation": "uses_data", "target_id": V_DATA}],
    {"protocol": "Exomiser 13.1.0 run on the 37 cases with database releases from February 2019 to February 2022. A variant is flagged when its human phenotype score increases by at least the stated difference between runs and its variant score exceeds the stated threshold. Each Exomiser variant is classified TP, FN, FP or TN against the diagnosed variants; recall, precision, F and F2 are derived in R 4.2.1. Fewer false positives means fewer candidates to review.",
     "version": "Supplementary Table 1", "denominator": 37,
     "source_locator": "Results paragraphs 5-6; Methods 'Reanalysis optimisation'; Supplementary Table 1",
     "limitations": ["Retrospective: the 37 cases were already diagnosed, so this measures recovery of known later diagnoses, not new diagnostic yield.",
                     "The database releases compared are not printed in the supplement; the row for 0.2 and 0.8 matches the text's February 2019 versus February 2022 comparison (claim).",
                     "Run by the Exomiser developers.", "The ACMG/AMP classifier condition reported in the text (precision 88%, recall 82%) is not in this table."],
     "missing_metadata": {"uncertainty": {"reason": "unreported"}}})
claim(f"{P}-claim-vestito2024-database-pair", VP, "compared_database_releases",
      "Results paragraph 6 reports that, comparing Exomiser results based on the February 2019 and February 2022 databases, a variant score above 0.8 with a human phenotype score increase of 0.2 highlights 54 new candidates in the 37 cases, 31 of them correct (recall 84%, precision 57%). Supplementary Table 1 prints TP 31 and FP 23 (31 + 23 = 54) for that setting, so the table is read as that comparison; the table itself does not name the releases.",
      S_VES, "Results paragraph 6; Supplementary Table 1 row 'Diff human score 0.2, Var score 0.8'")
claim(f"{P}-claim-vestito2024-review-reduction", VP, "candidates_to_review",
      "In the families investigated, the recommended setting reduces the number of candidates to review per case from a median of 30 (range 11-214) to one or two.",
      S_VES, "Results paragraph 6")
V_COMP = {"dataset_version": "37 later-diagnosed 100kGP cases", "split": "No split", "population": "1846 Exomiser candidate variants, 37 diagnosed",
          "inputs": "Original 100kGP VCFs; Exomiser 13.1.0 with database releases February 2019 to February 2022",
          "adaptation": "Threshold pair as stated per configuration", "metric_implementation": "Variant-level confusion counts in R 4.2.1",
          "aggregation": "All 37 cases pooled", "budget": None}
for line_no, t in rows:
    d, v = t[0], t[1]
    slug = f"dh{d.replace('0.', '')}-vs{v.replace('0.', '')}"
    cid = f"{P}-config-vestito2024-exomiser-13-1-0-{slug}"
    configuration(cid, f"Exomiser 13.1.0 reanalysis flag: phenotype score increase {d}, variant score {v} (Vestito et al. 2024)",
                  "Exomiser reanalysis filter flagging variants whose human phenotype score rose by the stated amount and whose variant score exceeds the stated threshold.",
                  EXOMISER, [S_VES, S_VES_SUPP], f"Diff human score {d}, Var score {v}", f"Supplementary Table 1 line {line_no}", "13.1.0",
                  f"Human phenotype score difference {d} between database releases; variant score threshold {v}; Exomiser default settings otherwise (Methods 'Reanalysis optimisation')")
    claims_rows.append([cid, S_VES_SUPP, f"Supplementary Table 1 line {line_no}, columns 'Diff human score' and 'Var score'", f"{d}; {v}", "configuration_attribute"])
    ev = f"{P}-eval-vestito2024-{slug}"
    evaluation(ev, f"Exomiser reanalysis flag {d}/{v}: later-diagnosed 100kGP cases", cid, VP, V_DATA, [S_VES, S_VES_SUPP], "author_reported", V_COMP,
               f"Supplementary Table 1 line {line_no}",
               extra={"limitations": ["Exomiser developers evaluating their own tool on retrospectively diagnosed cases."]})
    base = f"Supplementary Table 1 line {line_no} (Diff human score {d}, Var score {v})"
    for ti, col, metric, direction, unit, qual, rslug in [
            (2, "TP", "true-positive-count", "higher", "count", "diagnosed variants flagged", "tp"),
            (3, "FN", "false-negative-count", "lower", "count", "diagnosed variants not flagged", "fn"),
            (4, "FP", "false-positive-count", "lower", "count", "non-diagnostic variants flagged for review", "fp"),
            (5, "TN", "true-negative-count", "higher", "count", "non-diagnostic variants not flagged", "tn"),
            (6, "recall", "recall", "higher", "fraction", None, "recall"),
            (7, "precision", "precision", "higher", "fraction", None, "precision"),
            (8, "Fscore", "f1-score", "higher", "fraction", None, "f1"),
            (9, "F2score", "f-beta-score", "higher", "fraction", "F2 (beta = 2)", "f2")]:
        pv = t[ti]
        if not re.fullmatch(r"\d+(\.\d+)?", pv):
            raise SystemExit(f"Unparsed Vestito cell {pv!r}")
        result(f"{P}-result-vestito2024-{slug}-{rslug}", ev, S_VES_SUPP, f"{base}, column '{col}'", pv, format(Decimal(pv), "f"), metric,
               direction, unit, qualifier=qual, unit_detail="variants" if unit == "count" else None)

# ================================================================= relevance judgements
JUDGEMENTS = []
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
               "Do not combine these results with another protocol's results; cohorts, inputs and scoring units differ between sources."]


def judgement(short, pid, pname, relevance, endpoint, rationale, limitations, cites, group, title, headline, stratum=None, order=None):
    jid = f"use-case-mapping-rare-reanalysis-20261009-{short}"
    attrs = {"field": f"links:assessed_by:{pid}", "value": pid, "relevance": relevance, "endpoint": endpoint, "rationale": rationale,
             "constraints": CONSTRAINTS, "limitations": limitations,
             "citation_locators": [{"source_id": s, "locator": l} for s, l in cites],
             "source_locator": "; ".join(f"{s}: {l}" for s, l in cites), "revision": 1,
             "reason": "Recorded from the rare-disease reanalysis use-case pass 2026-10-09 (data/omics/use-case-coverage-rare-reanalysis-20261009). Draft until an independent review.",
             "comparison_group": group, "comparison_title": title, "headline_metric": headline}
    if stratum:
        attrs["stratum_label"], attrs["stratum_order"] = stratum, order
    rec(jid, "claim", f"Relevance of {pname} to \"{UC_NAME}\"", rationale, sorted({s for s, _ in cites}),
        [{"relation": "subject", "target_id": UC}], attrs, facets={})
    JUDGEMENTS.append({"judgement_id": jid, "protocol_id": pid, "relevance": relevance, "comparison_group": group,
                       **({"stratum_label": stratum, "stratum_order": order} if stratum else {})})


judgement("demidov2024-cnv-callers", DP, "CNV calls returned per caller in the Solve-RD exome reanalysis (Demidov et al. 2024)", "proxy",
          "Number of CNV calls each of three callers (ClinCNV, CoNIFER, ExomeDepth) returned to clinical experts for interpretation, by copy number and type, on the same 9171 unsolved exomes from 5757 families",
          "Three reanalysis callers run on the same unsolved cohort with the same downstream filters measure the review workload each adds, which is half of the use-case question. It is proxy evidence because the tables count calls to review, not new diagnoses per caller (those are printed only in the text), and thresholds differ by caller.",
          ["Workload only; per-caller new diagnoses appear only in the Results text (claim on the protocol).",
           "Thresholds differ by caller; ExomeDepth's Bayes factor threshold is printed two ways in Methods.",
           "ClinCNV was developed by a Solve-RD partner (author_reported).",
           "CNV reanalysis only; no SNV/indel reanalysis method compared."],
          [(S_DEM, "Table 1; Results 'Technical results' and 'Diagnostic results'"), (S_DEM_SUPP, "Supplementary Table 4")],
          "demidov2024-solverd-cnv", "CNV calls to review per caller, Solve-RD exome reanalysis (Demidov et al. 2024)", "count")
judgement("vestito2024-exomiser-thresholds", VP, "Exomiser reanalysis flag thresholds on later-diagnosed 100kGP cases (Vestito et al. 2024)", "proxy",
          "Variant-level TP, FN, FP, TN, recall, precision, F1 and F2 for 81 combinations of human phenotype score increase and variant score threshold, flagging new candidates between Exomiser database releases in 37 later-diagnosed cases",
          "Holding the knowledge update fixed and varying only the flagging rule measures how many new candidates must be reviewed to recover diagnoses that a database update makes visible, which bears on reducing review effort. It is proxy evidence: the 37 cases are known later diagnoses (reranking known solved cases does not establish new yield), the run is by the Exomiser developers, and the database pair is inferred from the text.",
          ["Known later-diagnosed cases; not new diagnostic yield.", "Exomiser developers evaluating their own tool.",
           "Database releases compared are inferred from the text (claim), not printed in the table.",
           "Thresholds were chosen on the same 37 cases, so the best row is optimistic."],
          [(S_VES_SUPP, "Supplementary Table 1"), (S_VES, "Results paragraphs 5-6; Methods 'Reanalysis optimisation'")],
          "vestito2024-exomiser-thresholds", "Exomiser reanalysis flag thresholds, later-diagnosed 100kGP cases (Vestito et al. 2024)", "f-beta-score")
TALOS_SRC = "uc-clinical-20260930-source-talos"
TALOS_T1 = "uc-clinical-20260930-source-talos-table1"
for order, (coh, mode, label) in enumerate([("acg", "trio", "ACG trio"), ("acg", "singleton", "ACG singleton"), ("acg", "full", "ACG full"),
                                            ("rgp", "trio", "RGP trio"), ("rgp", "singleton", "RGP singleton"), ("rgp", "full", "RGP full")], start=1):
    pid = f"uc-clinical-20260930-talos-{coh}-{mode}-protocol"
    judgement(f"talos2026-{coh}-{mode}", pid, f"Talos default versus strict filtering on known diagnoses, {label} (Talos 2026 Table 1)", "proxy",
              f"Known diagnoses recovered and candidate variants returned per proband by Talos default and strict (phenotype-match) filtering, {label} cohort",
              "Two Talos reanalysis configurations on the same reprocessed cohort show the trade-off between recovered diagnoses and candidates to review, which bears on reducing review effort. It is proxy evidence because the diagnoses were already known: reranking known solved cases does not establish new diagnostic yield.",
              ["Known diagnoses callable by the standardised pipeline; not new yield.", "Talos developers' own evaluation (author_reported).",
               "Candidates per proband are ratios of totals in the table and medians in the text (stored audit note).",
               "Already mapped as proxy for use-case-rare-disease-candidate-ranking; the evidence is the same records."],
              [(TALOS_T1, f"Table 1, {label} columns"), (TALOS_SRC, "Results; Table 1")],
              "talos2026-known-diagnoses", "Talos default and strict filtering on known diagnoses (Talos 2026)", "recall", label, order)
judgement("talos2026-exomiser-acg", "uc-clinical-20260930-exomiser-acg-protocol", "Exomiser v14 rank-budget recovery of known diagnoses in ACG trios (Talos 2026)", "proxy",
          "Known ACG trio diagnoses recovered by Exomiser v14 within all, top 10, top 5 and top 1 ranks, as the comparator to Talos",
          "A ranked-list reanalysis comparator on the same ACG trios shows how many candidates must be reviewed to recover known diagnoses, set against Talos's unranked short list. It is proxy evidence: the diagnoses were known, a rank budget is not measured reviewer effort, and the denominator conflict (194 in the text, 190 in the Extended Data Fig. 1 legend) is unresolved.",
          ["Known diagnoses; not new yield.", "Denominator 194 (text) versus 190 (Extended Data Fig. 1 legend) unresolved.",
           "Exomiser data release, phenotype input and pathogenicity sources not stated.", "Rank budget is not measured analyst effort."],
          [(TALOS_SRC, "Results 'Comparison with other tools'; Methods 'Exomiser comparison'; Extended Data Fig. 1 legend")],
          "talos2026-exomiser-acg", "Exomiser v14 rank budget on known ACG trio diagnoses (Talos 2026)", "recall")

# ================================================================= write
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate IDs: " + ", ".join(k for k, v in Counter(ids).items() if v > 1))
with open(f"{BATCH}/batch.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
claims_rows.sort(key=lambda r: (r[0], r[2]))
with open(f"{BATCH}/claims.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(claims_rows)
with open(f"{BATCH}/extract/judgements.json", "w", encoding="utf-8") as f:
    json.dump(JUDGEMENTS, f, indent=2, ensure_ascii=False)
print(json.dumps(Counter(r["kind"] for r in records), sort_keys=True))
