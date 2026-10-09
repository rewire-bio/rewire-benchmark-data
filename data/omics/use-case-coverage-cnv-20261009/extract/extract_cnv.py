"""Deterministic extraction of CNV caller comparison tables into a records batch.

Usage: python3 -I extract_cnv.py <download-dir> <batch-dir>

Reads the pinned XLSX tables and article XML, asserts the row and column labels
it depends on, and writes batch.jsonl and claims.csv. Each printed_value is the
shortest round-trip decimal of the stored cell value; the raw stored text is
kept in attributes.source_cell_text.
"""
import csv, json, os, sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
P = "cnv-20261009"
RETRIEVED = {
    "delavega": "2026-10-09T15:24:22Z",
    "gabrielaite": "2026-10-09T15:21:28Z",
    "nardone": "2026-10-09T15:28:17Z",
    "seqc2": "2026-10-09T15:25:50Z",
}
FACETS = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
EXTRACT_NOTE = ("Extracted by deterministic parse of the pinned XLSX cell XML (scripts in the batch "
                "retrieval log), with row and column labels asserted. printed_value is the shortest "
                "round-trip decimal of the stored cell value; source_cell_text keeps the raw stored text. "
                "Pending independent review.")
records, claims_rows = [], []


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="source_checked"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": FACETS if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def printed(raw):
    """Shortest round-trip decimal for numeric cells; text cells unchanged."""
    if raw in ("NA", "NaN"):
        return raw, None
    try:
        f = float(raw)
    except ValueError:
        return raw, None
    s = repr(f)
    if s.endswith(".0"):
        s = s[:-2]
    if "e" in s or "E" in s:
        s = format(Decimal(s), "f")
    return s, format(Decimal(s), "f")


def result(id_, eval_id, source_ids, locator, cell_text, metric, qualifier, extra=None, missing=None, unit="fraction"):
    pv, nv = printed(cell_text)
    if pv in ("NA", "NaN"):
        missing = dict(missing or {})
        missing["value"] = {"NA": "Printed NA; table footnote: no TP data to calculate metric",
                            "NaN": "Printed NaN; metric undefined in source, not zero"}[pv]
    attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": "higher", "unit": unit,
             "printed_value": pv, "numeric_value": nv, "uncertainty": None, "source_locator": locator,
             "source_cell_text": cell_text, "missing_metadata": missing or {"uncertainty": "Unreported"},
             "review": {"notes": EXTRACT_NOTE}}
    if extra:
        attrs.update(extra)
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric} ({qualifier})",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={}, status="needs_review")
    claims_rows.append([id_, source_ids[-1], locator, pv, "result"])


def evaluation(id_, name, config, protocol, dataset, source_ids, origin, comparison, locator, missing=None):
    rec(id_, "evaluation", name, "Published CNV caller comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "configuration", "target_id": config}, {"relation": "protocol", "target_id": protocol},
         {"relation": "dataset", "target_id": dataset}],
        {"origin": origin, "protocol": protocol, "version": "Primary source as retrieved 2026-10-09",
         "comparison": {"protocol_id": protocol, **comparison}, "published_score_reproduction": False,
         "source_locator": locator, "missing_metadata": missing or {}})


def claim(id_, subject, field, value, source_id, locator):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", [source_id],
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator, "review": {"notes": "Hand transcription from article XML text. Pending independent review."}},
        facets={}, status="needs_review")
    claims_rows.append([id_, source_id, locator, value, "claim"])


def sha(path):
    import hashlib
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def need(cells, coord, expected):
    got = cells.get(coord)
    if got != expected:
        raise SystemExit(f"Label check failed at {coord}: expected {expected!r}, got {got!r}")


# ---------------------------------------------------------------- sources
def source(id_, name, url, artifact_url, path, version, doi, retrieved, licence, extra=None, status="source_checked"):
    attrs = {"url": url, "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved,
             "artifact_sha256": sha(path), "doi": doi, "publication_status": "peer_reviewed", "licence": licence}
    attrs.update(extra or {})
    return rec(id_, "source", name, "Primary source retrieved and hashed for the CNV detection use-case pass.",
               [], [], attrs, status=status)


EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
dlv_x = f"{DL}/PMC12005901/article.xml"
dlv_s3 = f"{DL}/PMC12005901/x/sd/Supplemental_Table_3.xlsx"
gab_x = f"{DL}/gab/article.xml"
gab_s2 = f"{DL}/gab/x/s001/Supplementary Materials/Table S2.xlsx"
nar_x = f"{DL}/PMC12383524/article.xml"
nar_s1 = f"{DL}/PMC12383524/x/s/TableS1.xlsx"
sq_x = f"{DL}/PMC11188507/article.xml"

SRC_DLV, SRC_DLV_S3 = f"{P}-source-delavega2025", f"{P}-source-delavega2025-table-s3"
SRC_GAB, SRC_GAB_S2 = f"{P}-source-gabrielaite2021", f"{P}-source-gabrielaite2021-table-s2"
SRC_NAR, SRC_NAR_S1 = f"{P}-source-nardone2025", f"{P}-source-nardone2025-table-s1"
SRC_SQ = f"{P}-source-seqc2-somatic-cnv-2024"
SRC_BEH, SRC_BEH_T = "amp-source-dragen", "amp-source-dragen-supplementary-tables"

source(SRC_DLV, "Benchmarking of germline copy number variant callers from whole genome sequencing data for clinical applications",
       "https://doi.org/10.1093/bioadv/vbaf071", f"{EPMC}/PMC12005901/fullTextXML", dlv_x,
       "Bioinformatics Advances 5(1):vbaf071, published 2025-04-10; PMC12005901 full-text XML", "10.1093/bioadv/vbaf071",
       RETRIEVED["delavega"], "CC-BY-4.0", {"pmcid": "PMC12005901", "media_type": "application/xml"})
source(SRC_DLV_S3, "De La Vega et al. 2025, Supplemental Table 3",
       "https://doi.org/10.1093/bioadv/vbaf071", f"{EPMC}/PMC12005901/supplementaryFiles", dlv_s3,
       "Supplemental_Table_3.xlsx inside vbaf071_supplementary_data.zip", "10.1093/bioadv/vbaf071",
       RETRIEVED["delavega"], "CC-BY-4.0",
       {"container_sha256": {"europepmc_supplementary_zip": sha(f"{DL}/PMC12005901/supp.zip"),
                             "vbaf071_supplementary_data.zip": sha(f"{DL}/PMC12005901/x/vbaf071_supplementary_data.zip")},
        "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
source(SRC_GAB, "A Comparison of Tools for Copy-Number Variation Detection in Germline Whole Exome and Whole Genome Sequencing Data",
       "https://doi.org/10.3390/cancers13246283", f"{EPMC}/PMC8699073/fullTextXML", gab_x,
       "Cancers 13(24):6283, published 2021-12-14; PMC8699073 full-text XML", "10.3390/cancers13246283",
       RETRIEVED["gabrielaite"], "CC-BY-4.0", {"pmcid": "PMC8699073", "media_type": "application/xml"})
source(SRC_GAB_S2, "Gabrielaite et al. 2021, Table S2 (precision and recall of CNV calling tools)",
       "https://doi.org/10.3390/cancers13246283", f"{EPMC}/PMC8699073/supplementaryFiles", gab_s2,
       "Supplementary Materials/Table S2.xlsx inside cancers-13-06283-s001.zip", "10.3390/cancers13246283",
       RETRIEVED["gabrielaite"], "CC-BY-4.0",
       {"container_sha256": {"europepmc_supplementary_zip": sha(f"{DL}/gab/supp.zip"),
                             "cancers-13-06283-s001.zip": sha(f"{DL}/gab/x/cancers-13-06283-s001.zip")},
        "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"})
nar_concerns = [
    {"source_id": SRC_NAR_S1,
     "message": "Short-read input depth and alignment for Table S1 are stated inconsistently: Methods 2.2 says the 65x reads were subsampled to 25x and aligned with bwa-mem2 for preliminary evaluations; Results 3.1 says the HG002 data were previously aligned using the DRAGEN pipeline; the Data Availability Statement cites 30x Illumina HG002 2x250 reads. Which depth and aligner produced Table S1 is not resolved, so these results should not be compared automatically with other HG002 tables.",
     "source_locator": "Methods 2.2 paragraph 1; Results 3.1 paragraph 1; Data Availability Statement",
     "artifact_sha256": sha(nar_x), "reviewed_at": "2026-10-09T15:40:00Z", "review_method": "automated-source-review"},
]
nar_prose_concern = [
    {"source_id": SRC_NAR,
     "message": "Results 3.1 prose gives inGAP in the 5000-9999 bp bin as F1 97%, precision 92%, recall 94%. Table S1 rows for inGAP 5000-9999 print F1 0.9466, precision 0.9714, recall 0.9231. The prose values are not consistent with each other (F1 cannot exceed both precision and recall) or with the table. Table values are recorded; prose values are not.",
     "source_locator": "Results 3.1 paragraph 2 versus TableS1.xlsx Method inGAP, Interval 5000-9999",
     "artifact_sha256": sha(nar_x), "reviewed_at": "2026-10-09T15:40:00Z", "review_method": "automated-source-review"},
]
source(SRC_NAR, "A Hitchhiker Guide to Structural Variant Calling: A Comprehensive Benchmark Through Different Sequencing Technologies",
       "https://doi.org/10.3390/biomedicines13081949", f"{EPMC}/PMC12383524/fullTextXML", nar_x,
       "Biomedicines 13(8):1949, published 2025-08-09; PMC12383524 full-text XML", "10.3390/biomedicines13081949",
       RETRIEVED["nardone"], "CC-BY-4.0", {"pmcid": "PMC12383524", "media_type": "application/xml", "evidence_concerns": nar_prose_concern})
source(SRC_NAR_S1, "Nardone et al. 2025, Table S1 (ten short-read SV callers on HG002)",
       "https://doi.org/10.3390/biomedicines13081949", f"{EPMC}/PMC12383524/supplementaryFiles", nar_s1,
       "TableS1.xlsx inside biomedicines-13-01949-s001.zip", "10.3390/biomedicines13081949",
       RETRIEVED["nardone"], "CC-BY-4.0",
       {"container_sha256": {"europepmc_supplementary_zip": sha(f"{DL}/PMC12383524/supp.zip"),
                             "biomedicines-13-01949-s001.zip": sha(f"{DL}/PMC12383524/x/biomedicines-13-01949-s001.zip")},
        "media_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "evidence_concerns": nar_concerns})
source(SRC_SQ, "Evaluation of somatic copy number variation detection by NGS technologies and bioinformatics tools on a hyper-diploid cancer genome",
       "https://doi.org/10.1186/s13059-024-03294-8", f"{EPMC}/PMC11188507/fullTextXML", sq_x,
       "Genome Biology 25:163, published 2024-06-20; PMC11188507 full-text XML", "10.1186/s13059-024-03294-8",
       RETRIEVED["seqc2"], "CC-BY-4.0", {"pmcid": "PMC11188507", "media_type": "application/xml"}, status="discovered")

# ---------------------------------------------------------------- methods (tool families)
METHODS = {
    "dragen": ("DRAGEN", "Illumina DRAGEN secondary analysis platform; CNV and integrated CNV-SV callers.", "conventional_pipeline"),
    "cnvnator": ("CNVnator", "Read-depth CNV caller.", "conventional_pipeline"),
    "delly": ("DELLY", "Paired-end and split-read structural variant caller.", "conventional_pipeline"),
    "lumpy": ("LUMPY", "Probabilistic structural variant caller combining paired-end and split-read signals.", "conventional_pipeline"),
    "manta": ("Manta", "Paired-end and split-read structural variant caller.", "conventional_pipeline"),
    "parliament2": ("Parliament2", "Ensemble caller combining several structural variant callers.", "conventional_pipeline"),
    "cue": ("Cue", "Deep-learning structural variant caller operating on alignment-derived images.", "supervised_machine_learning"),
    "cn-mops": ("cn.MOPS", "Read-depth CNV caller using a mixture of Poissons across samples.", "conventional_pipeline"),
    "control-freec": ("Control-FREEC", "Read-depth copy-number caller.", "conventional_pipeline"),
    "gatk-gcnv": ("GATK gCNV", "GATK germline CNV caller with a panel-of-normals model.", "conventional_pipeline"),
    "clc-genomics-workbench": ("CLC Genomics Workbench CNV detection", "Commercial read-depth CNV workflow.", "conventional_pipeline"),
    "matchclip": ("MATCHCLIP", "Soft-clip based structural variant caller.", "conventional_pipeline"),
    "softsv": ("SoftSV", "Soft-clip based structural variant caller.", "conventional_pipeline"),
    "ingap": ("inGAP", "Structural variant caller (inGAP-sv).", "conventional_pipeline"),
    "wham": ("Wham", "Structural variant caller.", "conventional_pipeline"),
}
method_sources = {k: set() for k in METHODS}


def mid(k):
    return f"{P}-method-{k}"


def config(id_, name, method, version, source_ids, reported_name, missing=None, notes=None):
    method_sources[method].update(source_ids)
    attrs = {"entity_level": "method", "foundation_model": False, "reported_name": reported_name,
             "version": version, "missing_metadata": missing or {}}
    if notes:
        attrs["protocol"] = notes
    rec(id_, "configuration", name, f"{reported_name} as run in the cited comparison.", source_ids,
        [{"relation": "variant_of", "target_id": mid(method)}], attrs,
        facets={**FACETS, "method_types": [METHODS[method][2]]})


# ---------------------------------------------------------------- 1. DRAGEN (Behera et al.) Table S4
beh = rawxlsx.read(f"{DL}/dragen/moesm3.xlsx")["S4 CNV benchmarking"]
for c, v in {"A1": "Table S4: CNV benhmarking", "B4": "DRAGEN4.2 (CNV)", "F4": "DRAGEN4.2 (CNV+SV)", "J4": "CNVnator",
             "A5": "Length range", "B5": "Recall", "C5": "Precision", "D5": "F-score"}.items():
    need(beh, c, v)
BEH_BINS = {6: ("[1,000-5,000)", "1-5kb"), 7: ("[5,000-10,000)", "5-10kb"), 8: ("[10,000-20,0000)", "10-20kb"),
            9: ("[20,000-50,000)", "20-50kb"), 10: (">50,000", "gt50kb")}
for row, (label, _) in BEH_BINS.items():
    need(beh, f"A{row}", label)
BEH_CONFIGS = {"B": (f"{P}-config-behera2024-dragen42-cnv", "DRAGEN4.2 (CNV)", "dragen42-cnv"),
               "F": ("amp-config-dragen42-cnv-sv", "DRAGEN4.2 (CNV+SV)", "dragen42-cnv-sv"),
               "J": (f"{P}-config-behera2024-cnvnator", "CNVnator", "cnvnator")}
config(BEH_CONFIGS["B"][0], "DRAGEN 4.2 CNV-only configuration (Behera et al. Table S4)", "dragen",
       "Paper framework v4.2.4; supplement column label DRAGEN4.2 (CNV)", [SRC_BEH, SRC_BEH_T], "DRAGEN4.2 (CNV)",
       {"immutable_build": "Exact build hash unreported"}, "Depth-based CNV caller without the SV call set (Table S4 note contrasts it with CNV+SV)")
config(BEH_CONFIGS["J"][0], "CNVnator comparator (Behera et al. Table S4)", "cnvnator", None, [SRC_BEH, SRC_BEH_T], "CNVnator",
       {"version": "Table S4 header prints only 'CNVnator'. The AMP intake notes v0.4.1 from the article text; the article HTML was not re-read in this pass, so the version is left unset here."})
method_sources["dragen"].update([SRC_BEH, SRC_BEH_T])
DS_BEH = f"{P}-data-behera2024-hg002-giab-sv06-cnv-del-bins"
rec(DS_BEH, "dataset", "HG002 35x WGS, GIAB SV v0.6 deletions >1 kb, Table S4 length bins", "Benchmark sample and truth set for DRAGEN Table S4.",
    [SRC_BEH, SRC_BEH_T], [], {
        "version": "GIAB SV v0.6, GRCh37 reference for SV/CNV comparisons",
        "split": "Single HG002 benchmark sample; five length bins from 1 kb",
        "population": "HG002 Illumina NovaSeq 6000 2x151bp 35x WGS; truth restricted to >1 kb deletion records of GIAB SV v0.6 (per the AMP intake reading of Fig. 2f).",
        "source_locator": "Table S4 rows 6-10; Results CNV paragraph and Fig. 2f as recorded on amp-data-hg002-giab-sv06-cnv",
        "missing_metadata": {"denominator": "Per-bin truth, TP, FP and FN counts unreported in Table S4"},
        "related_dataset": "amp-data-hg002-giab-sv06-cnv"})
beh_protocols = {6: "amp-protocol-hg002-cnv-1-5kb"}
for row, (label, slug) in BEH_BINS.items():
    if row == 6:
        continue
    pid = f"{P}-protocol-behera2024-hg002-cnv-del-{slug}"
    beh_protocols[row] = pid
    rec(pid, "protocol", f"HG002 GIAB v0.6 CNV deletion {label} bp (DRAGEN Table S4)", "One length bin of the DRAGEN CNV benchmark.",
        [SRC_BEH, SRC_BEH_T], [{"relation": "dataset", "target_id": DS_BEH}], {
            "protocol": f"Compare copy-number calls to >1 kb deletion records in GIAB SV v0.6; length bin printed as {label}.",
            "version": f"Table S4 row {row}",
            "limitations": ["Deletions in one reference sample only; no duplication, tumour or clinical endpoint.",
                            "CNVnator values in Table S4 and in the article prose differ for the 1-5 kb bin (AMP intake); prose not re-read here."],
            "missing_metadata": {"denominator": "Per-bin counts unreported", "metric_implementation": "Exact CNV matching implementation unextracted"},
            **({"printed_label_note": "Row label prints '[10,000-20,0000)'; read as the 10-20 kb bin by position between [5,000-10,000) and [20,000-50,000). Printed label retained."} if row == 8 else {})})
BEH_METRIC = {0: ("recall", "Recall"), 1: ("precision", "Precision"), 2: ("f1-score", "F-score")}
for col, (cfg, label, cslug) in BEH_CONFIGS.items():
    cols = [chr(ord(col) + i) for i in range(3)]
    for row, (blabel, slug) in BEH_BINS.items():
        if col == "F" and row == 6:
            eid = "amp-eval-dragen-cnv-sv-1-5kb-fscore"
        else:
            eid = f"{P}-eval-behera2024-{cslug}-{slug}"
            ds = "amp-data-hg002-giab-sv06-cnv" if row == 6 else DS_BEH
            evaluation(eid, f"{label} deletion {blabel}", cfg, beh_protocols[row], ds,
                       [SRC_BEH, SRC_BEH_T], "independent_paper" if col == "J" else "author_reported",
                       {"dataset_version": "GIAB SV v0.6, GRCh37", "split": "Single HG002 benchmark sample", "population": f"HG002 35x; deletion truth in bin {blabel}, count unreported",
                        "inputs": "35x WGS alignments", "adaptation": None, "metric_implementation": None, "aggregation": "Single sample and length bin", "budget": None},
                       f"Supplementary Tables XLSX sheet 'S4 CNV benchmarking', columns {cols[0]}-{cols[2]}, row {row}",
                       {"denominator": "Unreported per bin", "metric_implementation": "Matching implementation unextracted"})
        for i, c in enumerate(cols):
            if col == "F" and row == 6 and i == 2:
                continue  # already stored as amp-result-dragen-cnv-sv-1-5kb-fscore
            need(beh, f"{c}5", BEH_METRIC[i][1])
            result(f"{P}-result-behera2024-{cslug}-{slug}-{BEH_METRIC[i][0]}", eid, [SRC_BEH, SRC_BEH_T],
                   f"Supplementary Tables XLSX sheet 'S4 CNV benchmarking', {c}{row}; row {blabel}; column {label} {BEH_METRIC[i][1]}",
                   beh[f"{c}{row}"], BEH_METRIC[i][0], f"deletions, {blabel} bp")

# ---------------------------------------------------------------- 2. De La Vega et al. 2025
s3 = rawxlsx.read(dlv_s3)["Supplemental_Table_3"]
need(s3, "A1", "Supplemental Table 3. Peformance of CNV callers across various event length sizes ")
need(s3, "A15", "NA: There was no TP data to calculate metric")
need(s3, "A5", "Caller")
GROUPS = [("B", "CNVs >=1kb and < 5kb", "Deletions", "deletions, 1-5 kb"), ("D", None, "Duplications", "duplications, 1-5 kb"),
          ("F", "CNVs >=5kb and <10kb", "Deletions", "deletions, 5-10 kb"), ("H", None, "Duplications", "duplications, 5-10 kb"),
          ("J", "CNVs >=10kb and <50kb", "Deletions", "deletions, 10-50 kb"), ("L", None, "Duplications", "duplications, 10-50 kb"),
          ("N", "CNVs >=50kb", "Deletions", "deletions, 50 kb and over"), ("P", None, "Duplications", "duplications, 50 kb and over"),
          ("R", " All size CNVs", "Deletions", "deletions, all sizes"), ("T", None, "Duplications", "duplications, all sizes"),
          ("V", "Combined Del/Dup", None, "deletions and duplications combined")]
for col, top, sub, _ in GROUPS:
    if top:
        need(s3, f"{col}3", top)
    if sub:
        need(s3, f"{col}4", sub)
    need(s3, f"{col}5", "Sensitivity")
    need(s3, f"{chr(ord(col) + 1)}5", "Precision")
DLV_ROWS = {
    6: ("Dragen v4.2 HS + Filters", "dragen42-hs-filters", "dragen", "DRAGEN 4.2 high-sensitivity mode with custom artifact filters (HS-F)", "4.2", None,
        "High-sensitivity mode (-sv-cnv-enable-high-sensitivity-mode=true) followed by the custom RTG vcffilter scheme in Supplementary File S1"),
    7: ("Dragen v4.2 HS", "dragen42-hs", "dragen", "DRAGEN 4.2 high-sensitivity mode (HS)", "4.2", None, "Integrated CNV-SV caller, high-sensitivity mode"),
    8: ("Dragen v4.2", "dragen42-default", "dragen", "DRAGEN 4.2 integrated CNV-SV caller, default parameters", "4.2", None, "Integrated CNV-SV caller, default parameters"),
    9: ("CNVnator (v0.4.1)", "cnvnator", "cnvnator", "CNVnator v0.4.1 (De La Vega et al.)", "v0.4.1", None, "Default settings from DRAGEN multi-genome BAM"),
    10: ("Cue (cue.v2.pt model)", "cue-v2", "cue", "Cue, cue.v2.pt model (De La Vega et al.)", "cue.v2.pt model", None, "Default settings from DRAGEN multi-genome BAM"),
    11: ("Delly (v1.1.6)", "delly", "delly", "DELLY (De La Vega et al.)", "Table S3 prints v1.1.6; Methods 2.3 prints v1.6",
         {"version": "Conflict: Table S3 row label 'Delly (v1.1.6)' versus Methods 2.3 'Delly v1.6'. Not resolved."}, "Default settings from DRAGEN multi-genome BAM"),
    12: ("Parliament 2", "parliament2", "parliament2", "Parliament2 (De La Vega et al.)", None, {"version": "Unreported in Table S3 and Methods 2.3"}, "Default settings from DRAGEN multi-genome BAM"),
    13: ("Lumpy", "lumpy", "lumpy", "LUMPY (De La Vega et al.)", "v0.2.13 (Methods 2.3; Table S3 row label prints no version)", None, "Default settings from DRAGEN multi-genome BAM"),
}
DS_DLV = f"{P}-data-delavega2025-hg002-giab-sv06-exons"
rec(DS_DLV, "dataset", "HG002 50x PCR-free WGS with GIAB SV v0.6 CNV truth and synthetic gene models", "Truth set for De La Vega et al. whole-genome benchmark.",
    [SRC_DLV, SRC_DLV_S3], [], {
        "version": "GIAB HG002 SV v0.6 on GRCh37 (hs37d5), insertions converted to duplications where >=95% identical to reference; 5,213 synthetic genes added",
        "split": "Single HG002 sample",
        "population": "HG002, PCR-free 2x150 bp NovaSeq 6000 to mean 50x, aligned to GRCh37 with the DRAGEN multi-genome aligner. Truth: 60 deletions and 10 duplications overlapping exons of canonical and synthetic transcripts (13 DEL and 4 DUP from GIAB plus 47 DEL and 6 DUP via synthetic genes); events 500 bp to 10 Mb.",
        "source_locator": "Methods 2.2, 2.4 paragraphs 1-3; Results 3.1 paragraphs 1-2",
        "missing_metadata": {"per_stratum_counts": "Truth and call counts per Table S3 stratum unreported"}})
PR_DLV = f"{P}-protocol-delavega2025-hg002-exon-overlap"
rec(PR_DLV, "protocol", "HG002 exon-overlap CNV benchmark by event type and length (De La Vega et al. Table S3)",
    "Clinical-style CNV scoring by coding-exon overlap and dosage direction.", [SRC_DLV, SRC_DLV_S3], [{"relation": "dataset", "target_id": DS_DLV}], {
        "protocol": "True positive: call overlaps at least 1 bp of a coding exon of a canonical or synthetic transcript (plus 15 bp intronic) and matches dosage direction; multi-exon events adjusted to avoid double counting; other calls false positive. Sensitivity and precision by GA4GH definitions. Strata by type and length as printed in Table S3.",
        "version": "Supplemental Table 3",
        "limitations": ["Single sample; truth relies on GIAB v0.6 and synthetic gene models placed by the authors.",
                        "Breakpoint accuracy and event length overlap are not scored.",
                        "Authors include employees of Tempus and Illumina (DRAGEN vendor), per the conflict-of-interest statement."],
        "missing_metadata": {"metric_implementation": "Evaluation code not identified in the article", "denominator": "Per-stratum counts unreported"}})
for row, (label, slug, method, name, version, missing, note) in DLV_ROWS.items():
    need(s3, f"A{row}", label)
    cfg = f"{P}-config-delavega2025-{slug}"
    config(cfg, name, method, version, [SRC_DLV, SRC_DLV_S3], label, missing, note)
    eid = f"{P}-eval-delavega2025-{slug}"
    evaluation(eid, f"{label} on HG002 exon-overlap benchmark", cfg, PR_DLV, DS_DLV, [SRC_DLV, SRC_DLV_S3],
               "author_reported" if method == "dragen" else "independent_paper",
               {"dataset_version": "GIAB HG002 SV v0.6 GRCh37 plus synthetic genes", "split": "Single HG002 sample",
                "population": "60 DEL and 10 DUP exon-overlapping truth events", "inputs": "50x PCR-free WGS, DRAGEN multi-genome BAM on GRCh37",
                "adaptation": None, "metric_implementation": None, "aggregation": "Single sample, per stratum", "budget": None},
               f"Supplemental Table 3, row {row} '{label}'",
               {"metric_implementation": "Evaluation code not identified", "denominator": "Per-stratum counts unreported",
                **({"origin_note": "DRAGEN developer (Illumina) employees are co-authors; recorded as author_reported"} if method == "dragen" else {})})
    for col, _, _, qual in GROUPS:
        for i, (metric, hdr) in enumerate([("recall", "Sensitivity"), ("precision", "Precision")]):
            c = chr(ord(col) + i)
            result(f"{eid.replace('-eval-', '-result-')}-{metric}-{c.lower()}", eid, [SRC_DLV, SRC_DLV_S3],
                   f"Supplemental Table 3, {c}{row}; row '{label}'; group '{qual}'; column {hdr}", s3[f"{c}{row}"], metric, qual)

# Table 1 (article XML): DRAGEN HS and HS-F precision on the virtual panel
import xml.etree.ElementTree as ET
t = ET.parse(dlv_x).getroot()
tw = [w for w in t.iter("table-wrap") if w.get("id") == "vbaf071-T1"][0]
txt = lambda e: " ".join("".join(e.itertext()).split())
rows = [[txt(c) for c in tr if c.tag in ("td", "th")] for tr in tw.iter("tr")]
assert rows[1] == ["No. of exons", "Precision HS (%)", "Precision HS-F (%)", "Length (kb)", "Precision HS (%)", "Precision HS-F (%)"], rows[1]
assert [r[0] for r in rows[2:]] == ["1", "2–5", ">5"] and [r[3] for r in rows[2:]] == ["0.5–1", "1–10", ">10"], rows
DS_COR = f"{P}-data-delavega2025-coriell-virtual-panel"
rec(DS_COR, "dataset", "25 Coriell cell lines with documented CNVs, 184-gene virtual panel", "Cell-line truth set for the De La Vega et al. virtual-panel evaluation.",
    [SRC_DLV], [], {
        "version": "Coriell catalogue annotations curated by the authors (Supplementary Table S1); 184-gene panel (Supplementary Table S2)",
        "split": "25 cell lines", "population": "PCR-free 50x WGS of 25 Coriell cell lines; evaluation limited to coding exons of 184 genes; putative false positives inspected and some added to the truth set; paralogous genes requiring specialised callers excluded.",
        "source_locator": "Methods 2.1, 2.4 paragraph 4; Results 3.2", "missing_metadata": {"truth_counts": "Per-stratum truth counts unreported in Table 1"}})
PR_COR = f"{P}-protocol-delavega2025-coriell-virtual-panel"
rec(PR_COR, "protocol", "Coriell virtual gene-panel CNV precision by exon count and length (De La Vega et al. Table 1)",
    "Precision of DRAGEN modalities within a 184-gene virtual panel.", [SRC_DLV], [{"relation": "dataset", "target_id": DS_COR}], {
        "protocol": "Exon-overlap and dosage-direction matching within the 184-gene panel; precision stratified by number of exons spanned and by event length.",
        "version": "Table 1",
        "limitations": ["Truth set curated partly by visual inspection of the same data, which can favour the evaluated caller.",
                        "Filtering scheme for HS-F was designed on these genes; the authors note possible overfitting (Discussion paragraph 7)."],
        "missing_metadata": {"sensitivity": "Table 1 prints precision only; Results 3.2 states 100% sensitivity across strata in prose", "denominator": "Unreported"}})
for key, col_ex, col_len, name in [("dragen42-hs", 1, 4, "Precision HS (%)"), ("dragen42-hs-filters", 2, 5, "Precision HS-F (%)")]:
    cfg = f"{P}-config-delavega2025-{key}"
    eid = f"{P}-eval-delavega2025-{key}-coriell-panel"
    evaluation(eid, f"{name.split()[1]} on Coriell virtual panel", cfg, PR_COR, DS_COR, [SRC_DLV], "author_reported",
               {"dataset_version": "Coriell annotations curated by authors", "split": "25 cell lines", "population": "Coding exons of 184 genes",
                "inputs": "50x PCR-free WGS", "adaptation": None, "metric_implementation": None, "aggregation": "Pooled across cell lines, per stratum", "budget": None},
               "Table 1", {"denominator": "Unreported", "origin_note": "DRAGEN developer (Illumina) employees are co-authors"})
    for r in rows[2:]:
        for col, qual in [(col_ex, f"exons spanned: {r[0]}"), (col_len, f"length: {r[3]} kb")]:
            v = r[col]
            rid = f"{eid.replace('-eval-', '-result-')}-{'exons' if col == col_ex else 'length'}-{r[0 if col == col_ex else 3].replace('–', '-').replace('>', 'gt').replace('.', 'p')}"
            pv = v
            nv = format(Decimal(v), "f")
            result(rid, eid, [SRC_DLV], f"Table 1, row '{r[0]}' / '{r[3]}', column '{name}' ({'exons spanned' if col == col_ex else 'CNV length'} block)",
                   pv, "precision", qual, unit="percent")

# ---------------------------------------------------------------- 3. Gabrielaite et al. 2021 Table S2, NA12878 WGS rows
g = rawxlsx.read(gab_s2)["Supplementary_table2"]
for c, v in zip("ABCDEFGHIJKL", ["sample", "tool", "library", "TP", "FP", "FN", "TP_FN", "N_truth", "N_DEL", "N_DUP", "precision", "recall"]):
    need(g, f"{c}1", v)
GAB_TOOLS = {"CLC": ("clc-genomics-workbench", "CLC Genomics Workbench", None), "cn.MOPS": ("cn-mops", "cn.MOPS", None),
             "CNVnator": ("cnvnator", "CNVnator", None), "ControlFREEC": ("control-freec", "Control-FREEC", "11.5"),
             "DELLY": ("delly", "DELLY", None), "Lumpy": ("lumpy", "LUMPY (lumpyexpress)", None),
             "GATK_gCNV": ("gatk-gcnv", "GATK gCNV", None), "Manta": ("manta", "Manta", None)}
DS_GAB = f"{P}-data-gabrielaite2021-na12878-wgs"
rec(DS_GAB, "dataset", "NA12878 WGS with the Haraksingh et al. 2017 gold-standard CNV set", "Gold-standard sample in the Gabrielaite et al. benchmark.",
    [SRC_GAB, SRC_GAB_S2], [], {
        "version": "Haraksingh et al. 2017 high-confidence NA12878 CNV list (2,076 CNVs, 51-453,313 bp)",
        "split": "Single sample (NA12878, sequenced in house)", "population": "NA12878 WGS, Nextera DNA Flex, NovaSeq 6000, >=30x, 150 bp reads, BWA-MEM 0.7.12 to hg19/GRCh37.",
        "source_locator": "Methods 2.1 and 2.5; Table S2 rows 'GB-WGS-NA12878'",
        "missing_metadata": {"exact_depth": "Methods state 'at least 30x' for WGS libraries"}})
PR_GAB = f"{P}-protocol-gabrielaite2021-na12878-wgs-overlap"
rec(PR_GAB, "protocol", "NA12878 WGS CNV recall and precision, 1 bp overlap (Gabrielaite et al. Table S2)",
    "Per-tool CNV calls on NA12878 WGS compared with the gold-standard CNV set.", [SRC_GAB, SRC_GAB_S2], [{"relation": "dataset", "target_id": DS_GAB}], {
        "protocol": "A call is a true positive if it overlaps a truth CNV by at least 1 bp; Recall = TP/(TP+FN), Precision = TP/(TP+FP). Default parameters; no confidence filtering except where the tool does it by default.",
        "version": "Table S2 rows with sample 'GB-WGS-NA12878'",
        "limitations": ["Manta and CNVnator were used to build the NA12878 truth set, which can favour them (Results 3.7).",
                        "1 bp overlap is a lenient match and ignores dosage direction in the stated formula.",
                        "Cohort rows GB-WGS-01 to 38 (SNP-array reference) and WES rows are not extracted in this pass."],
        "missing_metadata": {"dosage_direction": "Whether DEL/DUP type must match is not stated", "tool_versions": "Most tool versions unreported in the article"}})
na_rows = [r for r in range(2, 423) if g.get(f"A{r}") == "GB-WGS-NA12878"]
assert len(na_rows) == 8, na_rows
for r in na_rows:
    tool = g[f"B{r}"]
    assert g[f"C{r}"] == "WGS"
    slug, name, version = GAB_TOOLS[tool]
    cfg = f"{P}-config-gabrielaite2021-{slug}"
    config(cfg, f"{name} (Gabrielaite et al. WGS)", slug if slug in METHODS else slug, version, [SRC_GAB, SRC_GAB_S2], tool,
           None if version else {"version": "Unreported in the article methods"})
    eid = f"{P}-eval-gabrielaite2021-{slug}-na12878-wgs"
    evaluation(eid, f"{name} on NA12878 WGS", cfg, PR_GAB, DS_GAB, [SRC_GAB, SRC_GAB_S2], "independent_paper",
               {"dataset_version": "Haraksingh et al. 2017 NA12878 CNV set", "split": "Single sample", "population": "2,076 truth CNVs",
                "inputs": "NA12878 WGS >=30x, BWA-MEM hg19", "adaptation": None, "metric_implementation": None, "aggregation": "Single sample", "budget": None},
               f"Table S2.xlsx, sheet Supplementary_table2, row {r} (sample GB-WGS-NA12878, tool {tool})",
               {"metric_implementation": "CNVbench scripts referenced (github.com/cphgeno/CNVbench) but no commit cited"})
    counts = {"tp": g[f"D{r}"], "fp": g[f"E{r}"], "fn": g[f"F{r}"], "n_truth": g[f"H{r}"], "n_called_del": g[f"I{r}"], "n_called_dup": g[f"J{r}"]}
    for c, metric, denom in [("K", "precision", "TP+FP"), ("L", "recall", "TP+FN")]:
        result(f"{eid.replace('-eval-', '-result-')}-{metric}", eid, [SRC_GAB, SRC_GAB_S2],
               f"Table S2.xlsx, sheet Supplementary_table2, {c}{r}; sample GB-WGS-NA12878; tool {tool}; column {metric}",
               g[f"{c}{r}"], metric, "na12878 wgs, 1 bp overlap",
               extra={"scoring_conditions": {**counts, "denominator_formula": denom}},
               missing={"uncertainty": "Unreported"})

# ---------------------------------------------------------------- 4. Nardone et al. 2025 Table S1
n = rawxlsx.read(nar_s1)["TableS1"]
for c, v in zip("ABCDEFGHI", ["Method", "SV_Type", "Interval", "TP", "FP", "FN", "Precision", "Recall", "F1Score"]):
    need(n, f"{c}4", v)
NAR_TOOLS = {"Manta": ("manta", "v1.6.0"), "MATCHCLIP": ("matchclip", "v1"), "DELLY": ("delly", "v1.1.5"), "Lumpy": ("lumpy", "v0.2.13"),
             "SoftSV": ("softsv", "v1.4.2"), "inGAP": ("ingap", "v1.6.0"), "Wham": ("wham", "v1.7.0"), "CNVnator": ("cnvnator", "v0.4.1"),
             "DRAGENv4.0": ("dragen", "v4.0"), "DRAGENv4.2": ("dragen", "v4.2")}
DS_NAR = f"{P}-data-nardone2025-hg002-giab-sv06-tier1-del-hg38"
rec(DS_NAR, "dataset", "HG002 GIAB SV v0.6 Tier 1 deletions lifted to GRCh38 (5,414)", "Deletion truth set used by Nardone et al.",
    [SRC_NAR, SRC_NAR_S1], [], {
        "version": "GIAB NIST_SV_v0.6 HG002 Tier 1 deletions (5,465 on hg19) lifted to hg38 with CrossMap 0.7.3, 5,414 retained",
        "split": "Single HG002 sample", "population": "Public HG002 Illumina reads; depth and aligner for Table S1 stated inconsistently (see source evidence concern)",
        "source_locator": "Methods 2.1 and 2.2; Data Availability Statement",
        "missing_metadata": {"depth": "25x (Methods 2.2) versus 30x (Data Availability); unresolved", "aligner": "bwa-mem2 (Methods 2.2) versus DRAGEN pipeline (Results 3.1); unresolved"}})
PR_NAR = f"{P}-protocol-nardone2025-hg002-del-wittyer"
rec(PR_NAR, "protocol", "HG002 short-read deletion calling by length bin, witty.er (Nardone et al. Table S1)",
    "Deletion-only benchmark of ten short-read SV callers.", [SRC_NAR, SRC_NAR_S1], [{"relation": "dataset", "target_id": DS_NAR}], {
        "protocol": "Deletion calls compared with HG002 Tier 1 deletions using witty.er; TP, FP, FN, precision, recall and F1 per length bin and overall.",
        "version": "Table S1",
        "limitations": ["Deletions only; no duplications.", "Bins from 50 bp include events below usual CNV size; the CNV-relevant bins are 1,000 bp and above.",
                        "Input depth and aligner conflict between Methods, Results and Data Availability."],
        "missing_metadata": {"wittyer_version": "Unreported", "matching_parameters": "Unreported"}})
nar_rows = {}
for r in range(5, 85):
    nar_rows.setdefault(n[f"A{r}"], []).append(r)
assert set(nar_rows) == set(NAR_TOOLS) and all(len(v) == 8 for v in nar_rows.values()), {k: len(v) for k, v in nar_rows.items()}
BINS = ["50-99", "100-499", "500-999", "1000-4999", "5000-9999", "10000-19999", ">20000", "ALL"]
for tool, rws in nar_rows.items():
    method, version = NAR_TOOLS[tool]
    slug = tool.lower().replace("dragenv", "dragen-").replace(".", "-")
    cfg = f"{P}-config-nardone2025-{slug}"
    config(cfg, f"{tool} {version} (Nardone et al.)" if not tool.startswith("DRAGEN") else f"{tool} (Nardone et al.)", method, version,
           [SRC_NAR, SRC_NAR_S1], tool, None, "Default parameters" if not tool.startswith("DRAGEN") else "Commercial DRAGEN SV/CNV workflow; parameters unreported")
    eid = f"{P}-eval-nardone2025-{slug}"
    evaluation(eid, f"{tool} on HG002 deletions (Nardone et al.)", cfg, PR_NAR, DS_NAR, [SRC_NAR, SRC_NAR_S1], "independent_paper",
               {"dataset_version": "GIAB SV v0.6 Tier 1 deletions lifted to hg38", "split": "Single HG002 sample", "population": "5,414 truth deletions",
                "inputs": None, "adaptation": None, "metric_implementation": "witty.er (version unreported)", "aggregation": "Single sample, per length bin", "budget": None},
               f"TableS1.xlsx rows {rws[0]}-{rws[-1]} (Method {tool})",
               {"inputs": "Depth and aligner conflict; see source evidence concern"})
    assert [n[f"C{r}"] for r in rws] == BINS and all(n[f"B{r}"] == "DEL" for r in rws), tool
    for r in rws:
        b = n[f"C{r}"]
        counts = {"tp": n[f"D{r}"], "fp": n[f"E{r}"], "fn": n[f"F{r}"]}
        for c, metric, hdr in [("G", "precision", "Precision"), ("H", "recall", "Recall"), ("I", "f1-score", "F1Score")]:
            qual = "deletions, all sizes" if b == "ALL" else f"deletions, {b.replace('>', 'over ')} bp"
            result(f"{eid.replace('-eval-', '-result-')}-{metric}-{b.lower().replace('>', 'gt')}", eid, [SRC_NAR, SRC_NAR_S1],
                   f"TableS1.xlsx, {c}{r}; Method {tool}; Interval {b}; column {hdr}", n[f"{c}{r}"], metric, qual,
                   extra={"scoring_conditions": counts}, missing={"uncertainty": "Unreported"})

# ---------------------------------------------------------------- methods records
for k, (name, desc, _) in METHODS.items():
    srcs = sorted(method_sources[k])
    if not srcs:
        continue
    rec(mid(k), "method", name, desc, srcs, [], {"reported_name": name, "entity_level": "method",
        "source_locator": "Tool lists and table row labels of the cited sources", "missing_metadata": {"version": "Family record; versions are on configurations"}},
        facets={**FACETS, "method_types": [METHODS[k][2]]})

# ---------------------------------------------------------------- claims
claim(f"{P}-claim-cue-lower-size-limit", f"{P}-config-delavega2025-cue-v2", "detectable_event_length",
      "Cue (cue.v2.pt) did not detect events smaller than 5 kb, which the authors give as the lower limit of its training model.", SRC_DLV, "Results 3.1 paragraph 3 and paragraph 5")
claim(f"{P}-claim-dragen-hs-filters", f"{P}-config-delavega2025-dragen42-hs-filters", "post_processing",
      "HS-F removes calls under 500 bp or over 10 Mb, junction-only calls over 1 Mb, calls overlapping centromere or telomere gaps, and calls with >=90% reciprocal overlap with recurrent artifacts, using RTG vcffilter with a custom JavaScript.", SRC_DLV, "Methods 2.5")
claim(f"{P}-claim-na12878-truth-built-with-manta-cnvnator", DS_GAB, "truth_set_dependency",
      "Manta and CNVnator were used to generate the NA12878 truth CNV set, so their calls may be favoured.", SRC_GAB, "Results 3.7 paragraph 3")

# ---------------------------------------------------------------- discovered benchmark (no printed per-caller values)
rec(f"{P}-data-seqc2-hcc1395-cnv-benchmark", "dataset", "SEQC2 HCC1395 high-confidence somatic CNV call set", "Consensus somatic CNV set for the HCC1395/HCC1395BL pair.",
    [SRC_SQ], [], {"version": "Genome Biology 2024 Additional file 5 (VCF)", "split": "21 WGS and 12 WES replicates across six centres",
                   "source_locator": "Results; Table 1; Additional file 5", "missing_metadata": {"per_caller_values": "Per-caller precision and recall are shown only in figures"}}, status="discovered")
rec(f"{P}-benchmark-seqc2-hcc1395-somatic-cnv", "benchmark", "SEQC2 HCC1395 somatic CNV benchmark", "Benchmark of six somatic CNV callers on a hyper-diploid cancer cell line.",
    [SRC_SQ], [{"relation": "dataset", "target_id": f"{P}-data-seqc2-hcc1395-cnv-benchmark"}],
    {"entity_level": "suite", "version": "2024", "task": "Somatic copy-number gain, loss and LOH detection in tumour/normal WGS and WES",
     "scope_note": "Callers ascatNgs 4.2.1, CNVkit 0.9.1, Control-FREEC 11.6, DRAGEN 4.0.x, FACETS 0.6.0, HATCHet 1.0.4. Accuracy is reported in figures only; no results extracted.",
     "missing_metadata": {"printed_results": "No per-caller accuracy table in the article or Additional file 1"}}, status="discovered")

# ---------------------------------------------------------------- write
ids = [r["id"] for r in records]
dupes = {i for i in ids if ids.count(i) > 1}
assert not dupes, dupes
os.makedirs(BATCH, exist_ok=True)
with open(f"{BATCH}/batch.jsonl", "w") as f:
    for r in sorted(records, key=lambda r: r["id"]):
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
with open(f"{BATCH}/claims.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(sorted(claims_rows))
from collections import Counter
print(Counter(r["kind"] for r in records))
