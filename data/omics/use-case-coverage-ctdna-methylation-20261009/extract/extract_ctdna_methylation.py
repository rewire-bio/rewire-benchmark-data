"""Deterministic extraction of plasma cfDNA methylation comparison tables into a records batch.

Usage: python3 -I extract_ctdna_methylation.py <download-dir> <batch-dir>

Reads three pinned supplementary workbooks and asserts every row and column label it depends on:
  - Sun et al. 2024 (Genome Biology) Additional file 1, sheet 'Table S7 ', AUC block (H2:M9)
  - Giuili et al. 2025 (bioRxiv, DecoNFlow) Supplementary Table 3, sheets A and B (all cells)
  - Nguyen et al. 2023 (eLife, SPOT-MAS) Supplementary file 1, sheet 'Table S9' (all cells)
Supplementary Table 1 of Giuili et al. is read for the tool versions printed there.
Writes batch.jsonl and claims.csv. Each printed_value is the shortest round-trip decimal of the
stored cell value (text cells unchanged); the raw stored text is kept in raw_xml_value.
Records are written in the store form: single-meaning relations and declared attributes.
"""
import csv, hashlib, json, os, sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rawxlsx  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
P = "ctdnameth-20261009"
UC = "use-case-plasma-ctdna-methylation"
DATE = "2026-10-09"
CLIN = {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}
RES = {"areas": ["dna-genomes"], "contexts": ["research"]}
records, claim_rows = [], []


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def rec(id_, kind, name, description, source_ids, links=None, attributes=None, facets=None, status="needs_review"):
    r = {"id": id_, "kind": kind, "name": name, "description": description, "status": status,
         "facets": CLIN if facets is None else facets, "source_ids": source_ids,
         "links": links or [], "attributes": attributes or {}}
    records.append(r)
    return r


def printed(raw):
    """Shortest round-trip decimal for numeric cells; text cells unchanged."""
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


def number_formats(path, sheet):
    """Number format code applied to each cell of one sheet (General cells are omitted)."""
    import zipfile, xml.etree.ElementTree as ET
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
          "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
    rel = "{http://schemas.openxmlformats.org/package/2006/relationships}"
    z = zipfile.ZipFile(path)
    st = ET.fromstring(z.read("xl/styles.xml"))
    fmts = {n.get("numFmtId"): n.get("formatCode") for n in st.iter("{%s}numFmt" % ns["m"])}
    xfs = [x.get("numFmtId") for x in st.find("m:cellXfs", ns)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")).iter(rel + "Relationship")}
    out = {}
    for sh in wb.find("m:sheets", ns):
        if sh.get("name") != sheet:
            continue
        t = rels[sh.get("{%s}id" % ns["r"])]
        t = t.lstrip("/") if t.startswith("/") else "xl/" + t
        for c in ET.fromstring(z.read(t)).iter("{%s}c" % ns["m"]):
            code = fmts.get(xfs[int(c.get("s") or 0)])
            if code:
                out[c.get("r")] = code
    return out


def displayed(raw, code):
    """Text Excel shows for a numeric cell under a fixed-decimals format such as 0.0000."""
    from decimal import ROUND_HALF_UP
    core = code[:-2] if code and code.endswith("_ ") else code  # "_ " only pads the cell with a space
    if core is None or not core.startswith("0.") or set(core[2:]) != {"0"}:
        raise SystemExit(f"Unhandled number format {code!r}")
    return str(Decimal(raw).quantize(Decimal(1).scaleb(-(len(core) - 2)), rounding=ROUND_HALF_UP))


def expect(cells, ref, value, where):
    got = cells.get(ref)
    if got != value:
        raise SystemExit(f"{where} {ref}: expected {value!r}, found {got!r}")


# ---------------------------------------------------------------- sources
def source(id_, name, url, artifact_url, version, retrieved_at, path, doi, status, licence, media_type, extra=None):
    attrs = {"url": url, "artifact_url": artifact_url, "version": version, "retrieved_at": retrieved_at,
             "artifact_sha256": sha(path), "doi": doi, "publication_status": status, "licence": licence,
             "media_type": media_type, "source_locator": "Full artifact bytes; per-result locators on each result"}
    attrs.update(extra or {})
    rec(id_, "source", name, "Primary source retrieved and hashed for the plasma ctDNA methylation use-case pass.",
        [], attributes=attrs, facets=CLIN)


NCND = "CC-BY-NC-ND-4.0"
NOT_ARCHIVED = "Not archived in the batch: the licence (CC BY-NC-ND 4.0) does not permit redistribution beyond non-commercial verbatim copies; the hash pins the bytes read."

S_SUN = f"{P}-source-sun2024"
S_SUN_T = f"{P}-source-sun2024-additional-file-1"
S_GIU = f"{P}-source-giuili2025"
S_GIU_T1 = f"{P}-source-giuili2025-supp-table-1"
S_GIU_T3 = f"{P}-source-giuili2025-supp-table-3"
S_NGU = f"{P}-source-nguyen2023"
S_NGU_T = f"{P}-source-nguyen2023-supp-file-1"

source(S_SUN, "Systematic evaluation of methylation-based cell type deconvolution methods for plasma cell-free DNA",
       "https://doi.org/10.1186/s13059-024-03456-8",
       "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11660681/fullTextXML",
       "Genome Biology 25:318, published 2024-12-19; PMC11660681.1 full-text XML", "2026-10-09T19:58:16Z",
       f"{DL}/sun2024/PMC11660681.xml", "10.1186/s13059-024-03456-8", "peer_reviewed", NCND, "application/xml",
       {"archive_note": NOT_ARCHIVED})
source(S_SUN_T, "Sun et al. 2024, Additional file 1 (Tables S1-S8)",
       "https://doi.org/10.1186/s13059-024-03456-8",
       "https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-024-03456-8/MediaObjects/13059_2024_3456_MOESM1_ESM.xlsx",
       "Additional file 1 (13059_2024_3456_MOESM1_ESM.xlsx) of Genome Biology 25:318", "2026-10-09T19:58:22Z",
       f"{DL}/sun2024-supp/MOESM1.xlsx", "10.1186/s13059-024-03456-8", "peer_reviewed", NCND,
       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", {"archive_note": NOT_ARCHIVED})
source(S_GIU, "A benchmark of DNA methylation deconvolution methods for tumoral fraction estimation using DecoNFlow",
       "https://doi.org/10.1101/2025.11.27.688590",
       "https://www.biorxiv.org/content/10.1101/2025.11.27.688590v1.full.pdf",
       "bioRxiv preprint version 1, posted 2025-11-27; not peer reviewed", "2026-10-09T19:55:30Z",
       f"{DL}/deconflow/full.pdf", "10.1101/2025.11.27.688590", "preprint", NCND, "application/pdf",
       {"archive_note": NOT_ARCHIVED,
        "retrieval_note": "The bioRxiv JATS XML and the Europe PMC copy (PPR1127337) were not retrievable (HTTP 429, HTTP 500); the version 1 PDF was read through its text layer."})
source(S_GIU_T1, "Giuili et al. 2025, Supplementary Table 1 (deconvolution and DMR tools)",
       "https://doi.org/10.1101/2025.11.27.688590",
       "https://www.biorxiv.org/content/biorxiv/early/2025/11/27/2025.11.27.688590/DC3/embed/media-3.xlsx",
       "bioRxiv version 1 supplementary file media-3.xlsx", "2026-10-09T20:03:05Z",
       f"{DL}/deconflow-supp/media-3.xlsx", "10.1101/2025.11.27.688590", "preprint", NCND,
       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", {"archive_note": NOT_ARCHIVED})
source(S_GIU_T3, "Giuili et al. 2025, Supplementary Table 3 (median limit of detection)",
       "https://doi.org/10.1101/2025.11.27.688590",
       "https://www.biorxiv.org/content/biorxiv/early/2025/11/27/2025.11.27.688590/DC5/embed/media-5.xlsx",
       "bioRxiv version 1 supplementary file media-5.xlsx", "2026-10-09T19:56:05Z",
       f"{DL}/deconflow-supp/media-5.xlsx", "10.1101/2025.11.27.688590", "preprint", NCND,
       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
       {"archive_note": NOT_ARCHIVED,
        "evidence_concerns": [{
            "source_id": S_GIU_T3,
            "message": ("Sheet A, RRBS-CL columns K-O, disagree with sheet B and with Figure 4A of the preprint for five "
                        "tools. Sheet A prints UXM 0.003/0.003/0.001/0.003/0.001, MetDecode 0.003/0.003/0.003/0.003/0.001, "
                        "meth_atlas 0.5/0.25/0.25/0.25/0.25, PRMeth 0.1 at every depth and CIBERSORT 0.05/0.05/0.007/0.025/0.007. "
                        "Figure 4A prints these rows as UXM 0.05/0.05/0.007/0.025/0.007, MetDecode 0.003/0.003/0.001/0.003/0.001, "
                        "meth_atlas 0.003/0.003/0.003/0.003/0.001, PRMeth 0.5/0.25/0.25/0.25/0.25 and CIBERSORT 0.1 at every depth, "
                        "and sheet B's overall RRBS-CL medians (UXM 0.025, meth_atlas 0.003, PRMeth 0.25, CIBERSORT 0.1) fit the figure, "
                        "not sheet A. The Results text (MetDecode reaches its RRBS-CL plateau at 20M) fits sheet A. "
                        "The WGBS-TT and RRBS-TT columns agree with Figure 4A. Values are recorded as printed; which rows are "
                        "correct is not resolved."),
            "source_locator": "Supplementary Table 3 sheet A K4:O12 versus sheet B D3:D12 and preprint Figure 4A (page 12; caption printed as 'Figure 43') and Results paragraph on LoD",
            "artifact_sha256": sha(f"{DL}/deconflow-supp/media-5.xlsx"),
            "reviewed_at": "2026-10-09T20:30:00Z",
            "review_method": "ai-assisted-source-review"}]})
source(S_NGU, "Multimodal analysis of methylomics and fragmentomics in plasma cell-free DNA for multi-cancer early detection and localization",
       "https://doi.org/10.7554/eLife.89083",
       "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10567114/fullTextXML",
       "eLife 12:RP89083, version of record published 2023-10-11; PMC10567114 full-text XML", "2026-10-09T20:04:09Z",
       f"{DL}/spotmas/PMC10567114.xml", "10.7554/eLife.89083", "peer_reviewed", "CC-BY-4.0", "application/xml",
       {"archive_sha256": sha(f"{BATCH}/artifacts/nguyen2023-article.xml.gz"),
        "archive_note": "gzip -n -9 copy of the exact bytes in artifacts/nguyen2023-article.xml.gz (CC BY 4.0)"})
source(S_NGU_T, "Nguyen et al. 2023, Supplementary file 1 (Tables S1-S11)",
       "https://doi.org/10.7554/eLife.89083",
       "https://pmc-oa-opendata.s3.amazonaws.com/PMC10567114.1/elife-89083-supp1.xlsx",
       "Supplementary file 1 (elife-89083-supp1.xlsx) of eLife 12:RP89083, PMC open-access copy PMC10567114.1",
       "2026-10-09T20:03:58Z", f"{DL}/spotmas-supp/elife-89083-supp1.xlsx", "10.7554/eLife.89083", "peer_reviewed",
       "CC-BY-4.0", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
       {"archive_sha256": sha(f"{BATCH}/artifacts/nguyen2023-supplementary-file-1.xlsx.gz"),
        "archive_note": "gzip -n -9 copy of the exact bytes in artifacts/nguyen2023-supplementary-file-1.xlsx.gz (CC BY 4.0)",
        "evidence_concerns": [{
           "source_id": S_NGU_T,
           "message": ("Stage-stratum sizes in Table S9 differ from Table S8 and from article Table 1 for the same cohorts. "
                       "Discovery all-cancer n: Table S9 stage I 50, II 163, III 148, unknown stage 138; Table S8 52, 169, 150, 128. "
                       "Validation: Table S9 22, 58, 74, 85; Table S8 23, 69, 77, 70. Per-cancer all-stage n agree. Stage-stratum "
                       "accuracies are recorded as printed; their denominators are not reconciled."),
           "source_locator": "Supplementary file 1, Table S9 columns F, J, N, R versus Table S8 columns D, F, H, J (rows 5-10 and 14-19); article Table 1",
           "artifact_sha256": sha(f"{DL}/spotmas-supp/elife-89083-supp1.xlsx"),
           "reviewed_at": "2026-10-09T20:30:00Z",
           "review_method": "ai-assisted-source-review"}]})


def note(path, url):
    return {"method": ["deterministic-table-parse"], "reviewer": ["claude"], "date": DATE,
            "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
            "artifact_sha256": sha(path), "retrieval_url": url,
            "note": ("Extracted by deterministic parse of the pinned XLSX cell XML (extract/rawxlsx.py, "
                     "extract/extract_ctdna_methylation.py) with row and column labels asserted. printed_value is the "
                     "shortest round-trip decimal of the stored cell value, or the displayed text where the workbook "
                     "applies a fixed-decimals number format (recorded in workbook_number_format); raw_xml_value keeps the "
                     "stored text. Pending independent review.")}


def result(id_, eval_id, source_ids, locator, raw, metric, qualifier, unit, direction, review, extra=None, missing=None):
    pv, nv = printed(raw)
    attrs = {"metric": metric, "metric_qualifier": qualifier, "metric_direction": direction, "unit": unit,
             "printed_value": pv, "numeric_value": nv, "source_locator": locator, "raw_xml_value": raw,
             "review": review}
    miss = {"uncertainty": {"reason": "unreported"}}
    miss.update(missing or {})
    attrs["missing_metadata"] = miss
    attrs.update(extra or {})
    rec(id_, "result", f"{eval_id.replace(P + '-eval-', '')} {metric} ({qualifier})",
        "Reported measurement transcribed from the pinned source. Not independently reproduced.",
        source_ids, [{"relation": "evaluation", "target_id": eval_id}], attrs, facets={})
    claim_rows.append([id_, source_ids[-1], locator, pv, "result"])


def evaluation(id_, name, config, protocol, dataset, source_ids, origin, comparison, locator, facets, limitations=None, missing=None):
    attrs = {"origin": origin, "protocol": protocol, "version": "Primary source as retrieved 2026-10-09",
             "comparison": {"protocol_id": protocol, **comparison}, "source_locator": locator}
    if limitations:
        attrs["limitations"] = limitations
    if missing:
        attrs["missing_metadata"] = missing
    rec(id_, "evaluation", name, "Published comparison; transcribed, not reproduced.", source_ids,
        [{"relation": "system", "target_id": config}, {"relation": "assessment", "target_id": protocol},
         {"relation": "data", "target_id": dataset}], attrs, facets=facets)


def method(key, name, description, source_ids, access=None, facets=None, mtypes=("specialist",)):
    attrs = {"reported_name": name, "entity_level": "method",
             "source_locator": "Tool lists and table row labels of the cited sources",
             "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}
    if access:
        attrs["access"] = access
    f = dict(facets or CLIN)
    f["method_types"] = list(mtypes)
    rec(f"{P}-method-{key}", "method", name, description, source_ids, attributes=attrs, facets=f)
    return f"{P}-method-{key}"


def configuration(id_, name, method_id, source_ids, reported, version, locator, facets, mtypes=("specialist",), extra=None, missing=None):
    attrs = {"reported_name": reported, "foundation_model_eligible": False, "source_locator": locator}
    miss = dict(missing or {})
    if version:
        attrs["version"] = version
    else:
        miss.setdefault("version", {"reason": "unreported"})
    if miss:
        attrs["missing_metadata"] = miss
    attrs.update(extra or {})
    f = dict(facets)
    f["method_types"] = list(mtypes)
    rec(id_, "configuration", name, "Configuration as run in the cited comparison.", source_ids,
        [{"relation": "configuration_of", "target_id": method_id}], attrs, facets=f)


def claim(id_, subject, field, value, source_ids, locator, path, url):
    rec(id_, "claim", f"{field}: {subject}", "Descriptive fact transcribed from the pinned source.", source_ids,
        [{"relation": "subject", "target_id": subject}],
        {"field": field, "value": value, "source_locator": locator,
         "review": {"method": ["transcription"], "reviewer": ["claude"], "date": DATE,
                    "reviewer_note": "Claude (Opus 5.5) extraction agent; extraction record, not an independent review",
                    "artifact_sha256": sha(path), "retrieval_url": url,
                    "note": "Hand transcription from the article text. Pending independent review."}},
        facets={})
    claim_rows.append([id_, source_ids[-1], locator, value, "claim"])


# ---------------------------------------------------------------- shared methods
GH = "Code location as printed in the cited Methods: "
M = {
    "methatlas": method("methatlas", "MethAtlas (meth_atlas)", "Reference-based cfDNA deconvolution by non-negative least squares over CpG sites.",
                        [S_SUN, S_GIU_T1], GH + "https://github.com/nloyfer/meth_atlas (Sun et al. 2024 Methods). Licence not stated in the cited sources."),
    "cfnome": method("cfnome", "cfNOMe", "Reference-based cfDNA deconvolution by linear least squares.", [S_SUN],
                     GH + "https://github.com/FlorianErger/cfNOMe (Sun et al. 2024 Methods). Licence not stated in the cited source."),
    "celfie": method("celfie", "CelFiE", "Reference-based cfDNA deconvolution by expectation maximisation over methylated and total read counts, with optional unknown components.",
                     [S_SUN, S_GIU_T1], GH + "https://github.com/christacaggiano/celfie (Sun et al. 2024 Methods). Licence not stated in the cited sources."),
    "celfeer": method("celfeer", "CelFEER", "Read-level variant of the CelFiE model for cfDNA deconvolution.", [S_SUN],
                      GH + "https://github.com/pi-zz-a/CelFEER (Sun et al. 2024 Methods). Licence not stated in the cited source."),
    "uxm": method("uxm", "UXM", "Fragment-level reference-based deconvolution using the share of unmethylated fragments at marker regions.",
                  [S_SUN, S_GIU_T1], GH + "https://github.com/nloyfer/UXM_deconv (Sun et al. 2024 Methods). Licence not stated in the cited sources."),
    "houseman-cp": method("houseman-cp", "Houseman constrained projection (EpiDISH implementation)", "Constrained projection least-squares deconvolution (Houseman 2012), run through the EpiDISH R package.",
                          [S_GIU_T1], None, RES),
    "epidish-rpc": method("epidish-rpc", "EpiDISH robust partial correlations", "Robust partial correlation deconvolution from the EpiDISH R package.", [S_GIU_T1], None, RES),
    "cibersort": method("cibersort", "CIBERSORT (EpiDISH implementation)", "nu-support vector regression deconvolution, run through the EpiDISH R package.", [S_GIU_T1], None, RES),
    "episcore": method("episcore", "EpiSCORE", "Weighted robust partial correlation deconvolution.", [S_GIU_T1], None, RES),
    "prmeth": method("prmeth", "PRMeth", "Partially reference-based deconvolution by non-negative matrix factorisation.", [S_GIU_T1], None, RES),
    "metdecode": method("metdecode", "MetDecode", "Partially reference-based NNLS deconvolution with weighted error and learned unknown contributors.", [S_GIU_T1], None, RES),
    "spotmas-too": method("spotmas-too", "SPOT-MAS tissue-of-origin classifier", "Tissue-of-origin classification from nine SPOT-MAS cfDNA feature sets (targeted and genome-wide methylation, fragment length, copy number and end motifs) from one bisulfite library.",
                          [S_NGU], None, CLIN, ("supervised_machine_learning",)),
}

# ================================================================ Sun et al. 2024, Table S7 AUC block
sun_path = f"{DL}/sun2024-supp/MOESM1.xlsx"
sun_url = "https://static-content.springer.com/esm/art%3A10.1186%2Fs13059-024-03456-8/MediaObjects/13059_2024_3456_MOESM1_ESM.xlsx"
sun = rawxlsx.read(sun_path)["Table S7 "]
sun_fmt = number_formats(sun_path, "Table S7 ")
W = "Sun Additional file 1, sheet 'Table S7 '"
expect(sun, "A1", "Table S7: The evaluation metrics for real-world datasets", W)
expect(sun, "H2", "AUC values ", W)
expect(sun, "H3", "Datasets", W)
sun_cols = {"I": "celfeer", "J": "celfie", "K": "cfnome", "L": "methatlas", "M": "uxm"}
sun_labels = {"celfeer": "CelFEER", "celfie": "CelFiE", "cfnome": "cfNOMe", "methatlas": "MethAtlas", "uxm": "UXM"}
for col, key in sun_cols.items():
    expect(sun, f"{col}3", sun_labels[key], W)
sun_rows = {4: "Liver cancer (WGBS)", 5: "Liver cancer (cfMethyl-Seq)", 6: "Colon cancer", 7: "LUAD", 8: "LUSC", 9: "Gastric cancer"}
for r, label in sun_rows.items():
    expect(sun, f"H{r}", label, W)
    expect(sun, f"A{r}", label, W)
if any(k for k in sun if int("".join(c for c in k if c.isdigit())) > 9):
    raise SystemExit("Sun Table S7 has rows below row 9")

D_SUN_HCC = f"{P}-data-sun2024-hcc-plasma-wgbs"
D_SUN_CFM = f"{P}-data-sun2024-cfmethyl-seq-plasma"
rec(D_SUN_HCC, "dataset", "Plasma cfDNA WGBS, 24 liver cancer patients and 32 healthy individuals (EGAD00001000856)",
    "Real plasma cohort used by Sun et al. 2024 to test deconvolution-based disease detection.", [S_SUN],
    attributes={"version": "EGA EGAD00001000856 (Chan et al. 2013, PNAS) as reprocessed by Sun et al. 2024",
                "accession": "EGAD00001000856", "assay": "Plasma cfDNA whole-genome bisulfite sequencing; Bismark v0.24.2 alignment to hg38, deduplication, wgbstools pat files",
                "population": "24 liver cancer (hepatocellular carcinoma) patients and 32 healthy individuals",
                "positives": 24, "negatives": 32, "access": "Controlled access through EGA",
                "source_locator": "Sun et al. 2024, Methods 'Data collection and processing' (P30) and Results 'Evaluation of deconvolution results on real-world clinical settings' (P20)"})
rec(D_SUN_CFM, "dataset", "Plasma cfMethyl-Seq, 225 cancer patients and 193 healthy individuals (EGAD00001009003)",
    "Real plasma cohort used by Sun et al. 2024 to test deconvolution-based disease detection.", [S_SUN],
    attributes={"version": "EGA EGAD00001009003 (Stackpole et al. 2022, Nat Commun) as reprocessed by Sun et al. 2024",
                "accession": "EGAD00001009003", "assay": "Plasma cfMethyl-Seq; TrimGalore v0.6.10, Bismark v0.24.2 alignment to hg38, deduplication, wgbstools pat files",
                "population": "225 cancer patients (67 lung adenocarcinoma, 41 lung squamous cell carcinoma, 30 liver, 54 colon, 33 stomach) and 193 healthy individuals",
                "positives": 225, "negatives": 193, "access": "Controlled access through EGA",
                "scope_note": ("Same source study as amp-data-cfmethyl-408 (Stackpole et al. 2022), but the counts differ: that record has "
                               "217 cancers and 191 non-cancers passing QC. The two are not linked as the same data."),
                "source_locator": "Sun et al. 2024, Methods 'Data collection and processing' (P30)"})

PR_SUN_HCC = f"{P}-protocol-sun2024-hcc-wgbs-detection-auc"
PR_SUN_CFM = f"{P}-protocol-sun2024-cfmethyl-detection-auc"
SUN_PROTO = ("Deconvolve each plasma sample against a full 35-cell-type reference atlas with each method, then train a random "
             "forest on the estimated cell-type fractions to separate patients from healthy individuals and report ROC-AUC.")
SUN_LIM = ["The random forest training and evaluation split (cross-validation or held-out) is not stated; the AUC may be in-sample.",
           "Discrimination AUC, not sensitivity at a declared specificity.",
           "No uncertainty is reported for the AUC values."]
SUN_MISS = {"metric_implementation": {"reason": "unreported", "note": "Random forest settings and resampling not stated"},
            "split_seeds": {"reason": "unreported"}}
rec(PR_SUN_HCC, "protocol", "Sun et al. 2024 liver cancer detection from deconvolved plasma WGBS (ROC-AUC)",
    "Real-world disease detection test in Sun et al. 2024, liver cancer WGBS cohort.", [S_SUN, S_SUN_T],
    [{"relation": "uses_data", "target_id": D_SUN_HCC}],
    {"protocol": SUN_PROTO, "version": "Sun et al. 2024, Methods 'Assessment of deconvolution performance on real-world datasets' (P41)",
     "metric": "auroc", "metric_direction": "higher", "limitations": SUN_LIM, "missing_metadata": SUN_MISS,
     "source_locator": "Article P41; Additional file 1 Table S7 row 4"})
rec(PR_SUN_CFM, "protocol", "Sun et al. 2024 five-cancer detection from deconvolved plasma cfMethyl-Seq (ROC-AUC per cancer type)",
    "Real-world disease detection test in Sun et al. 2024, cfMethyl-Seq cohort; one AUC per cancer type against the same healthy group.",
    [S_SUN, S_SUN_T], [{"relation": "uses_data", "target_id": D_SUN_CFM}],
    {"protocol": SUN_PROTO + " One comparison per cancer type against the 193 healthy individuals.",
     "version": "Sun et al. 2024, Methods 'Assessment of deconvolution performance on real-world datasets' (P41)",
     "metric": "auroc", "metric_direction": "higher", "limitations": SUN_LIM, "missing_metadata": SUN_MISS,
     "source_locator": "Article P41; Additional file 1 Table S7 rows 5-9"})

sun_review = note(sun_path, sun_url)
SUN_CFG_NOTE = {"celfie": "Run with --unknowns 0 unless stated otherwise (Methods P33).",
                "celfeer": "Run with --unknowns 0 unless stated otherwise (Methods P33)."}
SUN_COUNTS = {5: ("liver cancer", 30), 6: ("colon cancer", 54), 7: ("lung adenocarcinoma", 67), 8: ("lung squamous cell carcinoma", 41), 9: ("gastric (stomach) cancer", 33)}
for col, key in sun_cols.items():
    cfg = f"{P}-config-sun2024-{key}"
    configuration(cfg, f"{sun_labels[key]} (Sun et al. 2024 benchmark)", M[key], [S_SUN, S_SUN_T], sun_labels[key], None,
                  "Additional file 1 Table S7 header; Methods 'Implementation of each cfDNA deconvolution method' (P33)", CLIN,
                  extra={"parameters": SUN_CFG_NOTE[key]} if key in SUN_CFG_NOTE else None,
                  missing={"version": {"reason": "unreported", "note": "Only GitHub repository URLs are given, without a release or commit"}})
    for proto, dataset, rows, tag in ((PR_SUN_HCC, D_SUN_HCC, [4], "hcc-wgbs"), (PR_SUN_CFM, D_SUN_CFM, [5, 6, 7, 8, 9], "cfmethyl")):
        ev = f"{P}-eval-sun2024-{key}-{tag}"
        pop = ("24 liver cancer vs 32 healthy, plasma WGBS" if tag == "hcc-wgbs"
               else "Each cancer type vs 193 healthy, plasma cfMethyl-Seq (225 cancers in five types)")
        evaluation(ev, f"{sun_labels[key]} deconvolution, disease detection AUC ({'liver cancer WGBS' if tag == 'hcc-wgbs' else 'cfMethyl-Seq cohort'})",
                   cfg, proto, dataset, [S_SUN, S_SUN_T], "independent_paper",
                   {"dataset_version": "Reprocessed by Sun et al. 2024 (hg38, Bismark v0.24.2)", "split": None, "population": pop,
                    "inputs": "Estimated fractions of 35 reference cell types from each deconvolution method",
                    "adaptation": None, "metric_implementation": None, "aggregation": "One AUC per cancer-type comparison", "budget": None},
                   f"Additional file 1 Table S7, column {col}, rows {rows[0]}-{rows[-1]}" if len(rows) > 1 else f"Additional file 1 Table S7, cell {col}{rows[0]}",
                   CLIN, limitations=["Random forest validation split not stated; see protocol limitations."],
                   missing={"comparison.split": {"reason": "unreported"}, "comparison.metric_implementation": {"reason": "unreported"}})
        for r in rows:
            label = sun_rows[r]
            if tag == "hcc-wgbs":
                qual, cnote = "liver cancer vs healthy; random forest on deconvolved cell-type fractions", "24 cases, 32 controls"
            else:
                name, n = SUN_COUNTS[r]
                qual = f"{name} vs healthy; random forest on deconvolved cell-type fractions"
                cnote = f"{n} cases, 193 controls"
            slug = label.lower().replace(" (wgbs)", "").replace(" (cfmethyl-seq)", "").replace(" ", "-")
            result(f"{P}-result-sun2024-{key}-{tag}-{slug}-auroc", ev, [S_SUN, S_SUN_T],
                   f"{W}, {col}{r}; row '{label}'; column '{sun_labels[key]}' under 'AUC values'",
                   sun[f"{col}{r}"], "auroc", qual, "unitless", "higher", sun_review,
                   extra={"denominator_note": cnote, **({"workbook_number_format": sun_fmt[f"{col}{r}"]} if f"{col}{r}" in sun_fmt else {})})
            if f"{col}{r}" in sun_fmt:
                records[-1]["attributes"]["printed_value"] = displayed(sun[f"{col}{r}"], sun_fmt[f"{col}{r}"])
                claim_rows[-1][3] = records[-1]["attributes"]["printed_value"]

claim(f"{P}-claim-sun2024-auc-definition", PR_SUN_CFM, "metric_definition",
      "ROC-AUC of random forest models for disease detection built with the estimated cell-type fractions from each deconvolution method as predictors; the reference atlas used all data of the 35 cell types.",
      [S_SUN], "Methods 'Assessment of deconvolution performance on real-world datasets' (P41)",
      f"{DL}/sun2024/PMC11660681.xml", "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11660681/fullTextXML")

# ================================================================ Giuili et al. 2025, Supplementary Table 3
g1 = rawxlsx.read(f"{DL}/deconflow-supp/media-3.xlsx")["1A"]
G1 = "Supplementary Table 1 sheet 1A"
expect(g1, "A1", "Method/Tool\xa0", G1)
expect(g1, "J1", "Version", G1)
expect(g1, "K1", "Container version", G1)
t1 = {"houseman-eq": 2, "houseman-ineq": 3, "cibersort": 4, "epidish-rpc": 5, "methatlas": 6, "episcore": 7,
      "prmeth": 8, "uxm": 9, "metdecode": 10, "celfie": 11}
t1_labels = {2: "Houseman's CP (with equality contrain)", 3: "Houseman's CP (with inequality contrain)", 4: "CIBERSORT",
             5: "EpiDISH ", 6: "meth_atlas", 7: "EpiSCORE", 8: "PRMeth", 9: "UXM", 10: "MetDecode", 11: "CelFiE"}
for r, label in t1_labels.items():
    expect(g1, f"A{r}", label, G1)

g3 = rawxlsx.read(f"{DL}/deconflow-supp/media-5.xlsx")
ga, gb = g3["A"], g3["B"]
fa = number_formats(f"{DL}/deconflow-supp/media-5.xlsx", "A")
fb = number_formats(f"{DL}/deconflow-supp/media-5.xlsx", "B")
GA, GB = "Supplementary Table 3 sheet A", "Supplementary Table 3 sheet B"
expect(ga, "B1", "RRBS-TT", GA); expect(ga, "G1", "WGBS-TT", GA); expect(ga, "K1", "RRBS-CL", GA)
depth_cols = {"B": ("rrbs-tt", "2M"), "C": ("rrbs-tt", "5M"), "D": ("rrbs-tt", "10M"), "E": ("rrbs-tt", "15M"), "F": ("rrbs-tt", "20M"),
              "G": ("wgbs-tt", "62M"), "H": ("wgbs-tt", "183M"), "I": ("wgbs-tt", "310M"), "J": ("wgbs-tt", "620M"),
              "K": ("rrbs-cl", "2M"), "L": ("rrbs-cl", "5M"), "M": ("rrbs-cl", "10M"), "N": ("rrbs-cl", "15M"), "O": ("rrbs-cl", "20M")}
for col, (_, depth) in depth_cols.items():
    expect(ga, f"{col}2", depth, GA)
a_rows = {3: "CelFiE", 4: "UXM", 5: "EpiDISH_CP_ineq", 6: "EpiDISH_CP_eq", 7: "MetDecode", 8: "meth_atlas", 9: "PRMeth",
          10: "EpiSCORE", 11: "EpiDISH_RPC", 12: "CIBERSORT"}
for r, label in a_rows.items():
    expect(ga, f"A{r}", label, GA)
expect(ga, "A13", "Median LoD per sequencing depth within each dataset", GA)
expect(ga, "B16", "Bold = best performance of the tool across sequencing depth", GA)
expect(ga, "B17", "* = best performance in the dataset", GA)
expect(gb, "A1", "Overall median LoD per dataset", GB)
b_cols = {"B": "wgbs-tt", "C": "rrbs-tt", "D": "rrbs-cl"}
expect(gb, "B2", "WGBS-TT", GB); expect(gb, "C2", "RRBS-TT", GB); expect(gb, "D2", "RRBS-CL", GB)
b_rows = {3: "CIBERSORT", 4: "CelFiE", 5: "EpiDISH_CP_eq", 6: "EpiDISH_CP_ineq", 7: "EpiDISH_RPC", 8: "EpiSCORE",
          9: "MetDecode", 10: "PRMeth", 11: "UXM", 12: "meth_atlas"}
for r, label in b_rows.items():
    expect(gb, f"A{r}", label, GB)
n_cells = len(ga) + len(gb)
if n_cells != 170 + 44:
    raise SystemExit(f"Unexpected cell count in Supplementary Table 3: {n_cells}")

label_key = {"CelFiE": "celfie", "UXM": "uxm", "EpiDISH_CP_ineq": "houseman-ineq", "EpiDISH_CP_eq": "houseman-eq",
             "MetDecode": "metdecode", "meth_atlas": "methatlas", "PRMeth": "prmeth", "EpiSCORE": "episcore",
             "EpiDISH_RPC": "epidish-rpc", "CIBERSORT": "cibersort"}
key_method = {"houseman-eq": M["houseman-cp"], "houseman-ineq": M["houseman-cp"], "cibersort": M["cibersort"],
              "epidish-rpc": M["epidish-rpc"], "methatlas": M["methatlas"], "episcore": M["episcore"], "prmeth": M["prmeth"],
              "uxm": M["uxm"], "metdecode": M["metdecode"], "celfie": M["celfie"]}
FIG_NAME = {"houseman-eq": "Houseman_eq", "houseman-ineq": "Houseman_ineq", "epidish-rpc": "EpiDISH"}

datasets = {
    "wgbs-tt": ("WGBS-TT", "1,640 WGBS in silico mixtures: tumour tissue reads (TCGA BLCA, BRCA, LUAD, LUSC) mixed into healthy plasma cfDNA reads",
                "Four depths (62M, 183M, 310M, 620M aligned reads), ten tumour fractions from 0.01% to 50% plus 0%, ten replicates each", 1640),
    "rrbs-tt": ("RRBS-TT", "1,550 RRBS in silico mixtures: lung, prostate and colorectal tumour tissue reads (PRJNA315188) mixed into healthy plasma cfDNA reads",
                "Five depths (2M, 5M, 10M, 15M, 20M aligned reads), ten tumour fractions from 0.01% to 50% plus 0%, ten replicates each", 1550),
    "rrbs-cl": ("RRBS-CL", "440 cfRRBS in silico mixtures: reads from neuroblastoma cell line CLB-GA artificial cfDNA mixed into healthy plasma cfDNA reads",
                "Five depths (2M, 5M, 10M, 15M, 20M aligned reads), tumour fractions from 0.01% to 50% plus 0%, ten replicates each", 440),
}
D_G, PR_G = {}, {}
LOD_RULE = ("Lowest tumour fraction at which the estimated fractions of the ten replicates are significantly higher than those "
            "of 0% tumour samples (one-tailed unpaired Mann-Whitney U test, Benjamini-Hochberg adjusted p < 0.01), "
            "moving from higher to lower fractions; tested grid 0.0001, 0.001, 0.003, 0.007, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5.")
for ds, (label, pop, split, n) in datasets.items():
    D_G[ds] = f"{P}-data-giuili2025-{ds}-in-silico-mixtures"
    rec(D_G[ds], "dataset", f"DecoNFlow benchmark {label} in silico mixtures",
        "In silico tumour-in-plasma read mixtures with known tumour fraction (Giuili et al. 2025).", [S_GIU],
        attributes={"version": "bioRxiv version 1 (2025-11-27); mixtures generated with SillyMix v1.1.0",
                    "population": pop, "split": split, "total": n,
                    "scope_note": ("Proxy for patient plasma: tumour reads come from tissue or a cell line, not from patient cfDNA. "
                                   "The abstract gives 3,690 mixtures in total; the three dataset counts in Results sum to 3,630."),
                    "source_locator": "Preprint Results 'Benchmarking datasets generation' (page 5); Methods; Supplementary Table 2D"},
        facets=RES)
    PR_G[ds] = f"{P}-protocol-giuili2025-{ds}-tumour-fraction-lod"
    rec(PR_G[ds], "protocol", f"DecoNFlow {label} tumour-fraction limit of detection",
        f"Median limit of detection of the tumour fraction for reference-based deconvolution tools on the {label} mixtures.",
        [S_GIU, S_GIU_T3], [{"relation": "uses_data", "target_id": D_G[ds]}],
        {"protocol": ("Build a reference of tumour and healthy cfDNA samples, select the top 250 hypomethylated DMRs per entity "
                      "(adjusted p < 0.01) with each of limma, DMRfinder and wgbstools, deconvolve every mixture with each tool, "
                      "then compute the limit of detection per combination. " + LOD_RULE),
         "version": "Preprint version 1, Methods 'Evaluation metrics and missing values'; DecoNFlow v2.2.0",
         "metric": "limit-of-detection", "metric_direction": "lower", "unit": "fraction",
         "unit_detail": "Tumour DNA fraction of the mixture (0.007 means 0.7%)",
         "aggregation": "Median over the combinations analysed (tumour types and DMR selection tools); the pooled combinations are not listed in the table",
         "limitations": ["In silico mixtures, not patient plasma.",
                         "Values are medians on a discrete grid of tested fractions; medians can fall between grid points.",
                         "The table does not state which combinations each median pools.",
                         "Preprint, not peer reviewed."],
         "source_locator": "Preprint Methods 'Evaluation metrics and missing values' (pages 26-27) and Figure 4 legend; Supplementary Table 3"},
        facets=RES)
claim(f"{P}-claim-giuili2025-lod-definition", PR_G["wgbs-tt"], "metric_definition", LOD_RULE.replace("; tested grid", ". Tested grid (Supplementary Table 2D):"),
      [S_GIU], "Preprint Results 'The tumoral fraction limit of detection' (page 11), Methods 'Evaluation metrics and missing values' (pages 26-27), Supplementary Table 2D",
      f"{DL}/deconflow/full.pdf", "https://www.biorxiv.org/content/10.1101/2025.11.27.688590v1.full.pdf")

g_review = note(f"{DL}/deconflow-supp/media-5.xlsx", "https://www.biorxiv.org/content/biorxiv/early/2025/11/27/2025.11.27.688590/DC5/embed/media-5.xlsx")
for ar, label in a_rows.items():
    key = label_key[label]
    t1r = t1[key]
    ver = g1[f"J{t1r}"]
    cfg = f"{P}-config-giuili2025-{key}"
    identity = None
    if key in FIG_NAME:
        identity = (f"Printed as {label} in Supplementary Table 3 and as {FIG_NAME[key]} in the preprint text and figures. "
                    "The match rests on Supplementary Table 1A (Houseman's CP with equality or inequality constraint and EpiDISH RPC "
                    "all run from the EpiDISH package) and on identical WGBS-TT and RRBS-TT values in Table 3 and Figure 4A.")
    miss = {}
    if ver == "No version":
        miss["version"] = {"reason": "unreported", "note": "Supplementary Table 1A prints 'No version'"}
    extra = {"environment": {"container": g1[f"K{t1r}"]}, "source_label": label}
    if identity:
        extra["model_identity_note"] = identity
    if key == "houseman-eq":
        extra["parameters"] = "Constrained projection with equality constraint (EpiDISH)"
    if key == "houseman-ineq":
        extra["parameters"] = "Constrained projection with inequality constraint (EpiDISH)"
    configuration(cfg, f"{label} (DecoNFlow benchmark)", key_method[key], [S_GIU, S_GIU_T1, S_GIU_T3], label,
                  None if ver == "No version" else ver,
                  f"Supplementary Table 1A row {t1r} ('{t1_labels[t1r].strip()}'); Supplementary Table 3 row label", RES,
                  extra=extra, missing=miss or None)
    for ds in ("wgbs-tt", "rrbs-tt", "rrbs-cl"):
        ev = f"{P}-eval-giuili2025-{key}-{ds}"
        cols = [c for c, (d, _) in depth_cols.items() if d == ds]
        br = [r for r, l in b_rows.items() if l == label][0]
        bc = [c for c, d in b_cols.items() if d == ds][0]
        lim = ["Tool run by the benchmark authors inside DecoNFlow containers; the tool is cited to an earlier publication, not introduced in this preprint."]
        if ds == "rrbs-cl" and key in ("uxm", "metdecode", "methatlas", "prmeth", "cibersort"):
            lim.append("Sheet A RRBS-CL values for this tool conflict with Figure 4A and sheet B (source evidence concern).")
        evaluation(ev, f"{label} tumour-fraction LoD ({datasets[ds][0]})", cfg, PR_G[ds], D_G[ds], [S_GIU, S_GIU_T3],
                   "independent_paper",
                   {"dataset_version": "bioRxiv version 1 mixtures", "split": datasets[ds][2],
                    "population": datasets[ds][1], "inputs": "Aligned bisulfite reads of each mixture; reference DMR matrix from three DMR tools",
                    "adaptation": None, "metric_implementation": LOD_RULE.split(";")[0],
                    "aggregation": "Median over combinations at each sequencing depth (sheet A) and overall per dataset (sheet B)",
                    "budget": None},
                   f"Supplementary Table 3 sheet A row {ar} columns {cols[0]}-{cols[-1]}; sheet B cell {bc}{br}", RES,
                   limitations=lim)
        for c in cols:
            depth = depth_cols[c][1]
            raw = ga[f"{c}{ar}"]
            extra = {"unit_detail": "Tumour DNA fraction of the mixture"}
            if raw.endswith("*"):
                extra["scope_note"] = "Text cell; the asterisk marks the best performance in the dataset (sheet A footnote B17)."
            else:
                extra["workbook_number_format"] = fa[f"{c}{ar}"]
            result(f"{P}-result-giuili2025-{key}-{ds}-{depth.lower()}-lod", ev, [S_GIU, S_GIU_T3],
                   f"{GA}, {c}{ar}; row '{label}'; column '{depth}' under '{datasets[ds][0]}'",
                   raw, "limit-of-detection", f"median at {depth} aligned reads", "fraction", "lower", g_review,
                   extra=extra)
            pv = records[-1]["attributes"]
            if raw.endswith("*"):
                pv["printed_value"] = raw
                pv["numeric_value"] = printed(raw[:-1])[1]
            else:
                pv["printed_value"] = displayed(raw, fa[f"{c}{ar}"])
            claim_rows[-1][3] = pv["printed_value"]
        result(f"{P}-result-giuili2025-{key}-{ds}-overall-lod", ev, [S_GIU, S_GIU_T3],
               f"{GB}, {bc}{br}; row '{label}'; column '{datasets[ds][0]}'",
               gb[f"{bc}{br}"], "limit-of-detection", "overall median across sequencing depths", "fraction", "lower", g_review,
               extra={"unit_detail": "Tumour DNA fraction of the mixture", "workbook_number_format": fb[f"{bc}{br}"]})
        records[-1]["attributes"]["printed_value"] = displayed(gb[f"{bc}{br}"], fb[f"{bc}{br}"])
        claim_rows[-1][3] = records[-1]["attributes"]["printed_value"]

# ================================================================ Nguyen et al. 2023, Table S9
n_path = f"{DL}/spotmas-supp/elife-89083-supp1.xlsx"
n_url = "https://pmc-oa-opendata.s3.amazonaws.com/PMC10567114.1/elife-89083-supp1.xlsx"
s9 = rawxlsx.read(n_path)["Table S9"]
if number_formats(n_path, "Table S9"):
    raise SystemExit("Table S9 cells carry a number format; printed_value would differ from the stored value")
N9 = "Supplementary file 1, sheet 'Table S9'"
expect(s9, "A1", "Table S9 The accurracy of RF, DNN and GCNN model for tissue of origin identification", N9)
blocks = {"discovery": (2, 3, 4, range(5, 11)), "validation": (11, 12, 13, range(14, 20))}
expect(s9, "B2", "Discovery", N9); expect(s9, "B11", "Validation", N9)
strata = {"B": ("all-stage", "All stage"), "F": ("stage-i", "Stage I"), "J": ("stage-ii", "Stage II"),
          "N": ("stage-iii", "Stage III"), "R": ("unknown-stage", "Non-metastasis with unknown stage")}
models = ["RF", "DNN", "GCNN"]
cancers = ["Breast", "CRC", "Gastric", "Liver", "Lung", "All cancer"]
cancer_name = {"Breast": "breast cancer", "CRC": "colorectal cancer", "Gastric": "gastric cancer", "Liver": "liver cancer", "Lung": "lung cancer"}
for blk, (hr, sr, mr, rows) in blocks.items():
    expect(s9, f"A{hr}", "Cancer type", N9)
    for c, (_, lab) in strata.items():
        expect(s9, f"{c}{sr}", lab, N9)
        expect(s9, f"{c}{mr}", "n", N9)
    for i, r in enumerate(rows):
        expect(s9, f"A{r}", cancers[i], N9)


def col_shift(c, k):
    n = 0
    for ch in c:
        n = n * 26 + ord(ch) - 64
    n += k
    s = ""
    while n:
        n, rem = divmod(n - 1, 26)
        s = chr(65 + rem) + s
    return s


for blk, (hr, sr, mr, rows) in blocks.items():
    for c in strata:
        for k, m in enumerate(models, start=1):
            expect(s9, f"{col_shift(c, k)}{mr}", m, N9)
if len(s9) != 307:
    raise SystemExit(f"Unexpected cell count in Table S9: {len(s9)}")

D_N = {"discovery": f"{P}-data-nguyen2023-spotmas-discovery-cancers", "validation": f"{P}-data-nguyen2023-spotmas-validation-cancers"}
rec(D_N["discovery"], "dataset", "SPOT-MAS discovery cohort, 499 non-metastatic cancer patients (five cancer types)",
    "Cancer cases of the SPOT-MAS discovery cohort used for tissue-of-origin classification.", [S_NGU, S_NGU_T],
    attributes={"version": "eLife 12:RP89083 (2023)",
                "population": "499 treatment-naive non-metastatic patients: 156 breast, 106 colorectal, 67 gastric, 77 liver, 93 lung; recruited in Vietnam",
                "split": "10-fold cross-validation within the discovery cohort", "total": 499,
                "assay": "SPOT-MAS: one plasma cfDNA bisulfite library; 450-region target capture (~52x) and shallow genome-wide fraction (~0.55x)",
                "source_locator": "Article Results 'Clinical characteristics' (P6-P7), 'The multimodal SPOT-MAS assay' (P9); Table 1; Supplementary file 1 Table S9"})
rec(D_N["validation"], "dataset", "SPOT-MAS validation cohort, 239 non-metastatic cancer patients (five cancer types)",
    "Cancer cases of the independent SPOT-MAS validation cohort used for tissue-of-origin classification.", [S_NGU, S_NGU_T],
    attributes={"version": "eLife 12:RP89083 (2023)",
                "population": "239 treatment-naive non-metastatic patients: 67 breast, 53 colorectal, 31 gastric, 45 liver, 43 lung; recruited in Vietnam",
                "split": "Random assignment of participants to discovery and validation cohorts; validation used only for evaluation", "total": 239,
                "assay": "SPOT-MAS: one plasma cfDNA bisulfite library; 450-region target capture (~52x) and shallow genome-wide fraction (~0.55x)",
                "source_locator": "Article Results 'Clinical characteristics' (P6, P8); Table 1; Supplementary file 1 Table S9"})
PR_N = {"discovery": f"{P}-protocol-nguyen2023-spotmas-too-discovery-cv", "validation": f"{P}-protocol-nguyen2023-spotmas-too-validation"}
TOO_PROTO = ("Classify each cancer patient's plasma into one of five cancer types (breast, colorectal, gastric, liver, lung) from "
             "nine concatenated SPOT-MAS feature sets; report the proportion of patients assigned to the correct type, "
             "overall and per cancer type and stage.")
TOO_LIM = ["Cancer patients only; no healthy or other-cancer samples are classified, so false localisations in non-cancer plasma are not measured.",
           "Features combine methylation with fragment length, copy number and end-motif signals; not a methylation-only workflow.",
           "Author-reported by the assay developer (Gene Solutions); no independent replication.",
           "Stage-stratum sizes in Table S9 conflict with Table S8 and Table 1 (source evidence concern)."]
rec(PR_N["discovery"], "protocol", "SPOT-MAS five-class tissue of origin, discovery cohort 10-fold cross-validation",
    "Tissue-of-origin accuracy within the discovery cohort.", [S_NGU, S_NGU_T],
    [{"relation": "uses_data", "target_id": D_N["discovery"]}],
    {"protocol": TOO_PROTO + " Discovery cohort, 10-fold cross-validation.", "version": "eLife 12:RP89083, Methods 'Construction of models for TOO'",
     "metric": "accuracy", "metric_direction": "higher", "limitations": TOO_LIM,
     "source_locator": "Article Methods 'Construction of models for TOO' (P49-P53); Supplementary file 1 Table S9 rows 2-10"})
rec(PR_N["validation"], "protocol", "SPOT-MAS five-class tissue of origin, independent validation cohort",
    "Tissue-of-origin accuracy of the discovery-trained models on the validation cohort.", [S_NGU, S_NGU_T],
    [{"relation": "uses_data", "target_id": D_N["validation"]}],
    {"protocol": TOO_PROTO + " Models trained on the discovery cohort, applied once to the validation cohort.",
     "version": "eLife 12:RP89083, Methods 'Construction of models for TOO'",
     "metric": "accuracy", "metric_direction": "higher", "limitations": TOO_LIM,
     "source_locator": "Article Methods 'Construction of models for TOO' (P49-P53); Supplementary file 1 Table S9 rows 11-19"})
claim(f"{P}-claim-nguyen2023-too-features", M["spotmas-too"], "input_features",
      "The tissue-of-origin models take the nine SPOT-MAS cfDNA feature sets (targeted methylation, genome-wide methylation, fragment length, short, long, total and ratio fragment features, copy number aberrations and end motifs) concatenated into one data frame.",
      [S_NGU], "Results 'SPOT-MAS enables prediction of cancer types' (P23); Results P9", f"{DL}/spotmas/PMC10567114.xml",
      "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10567114/fullTextXML")

cfg_n = {
    "RF": ("rf", "Random forest", "scikit-learn v1.0.2 GridSearchCV (CV 3, class_weight balanced)", None),
    "DNN": ("dnn", "Deep neural network", "H2O package version 3.36.1.2",
            "Printed as DNN in Table S9 and Methods 'Strategy 2: DNN model' (H2O multi-layer feedforward network), but Results P23 and Figure 8 figure supplement 1 call the second model a convolutional neural network (CNN)."),
    "GCNN": ("gcnn", "Graph convolutional neural network", None, None),
}
n_review = note(n_path, n_url)
for m, (mk, mname, ver, ident) in cfg_n.items():
    cfg = f"{P}-config-nguyen2023-spotmas-too-{mk}"
    extra = {"source_label": m}
    if ident:
        extra["model_identity_note"] = ident
    if m == "GCNN":
        extra["parameters"] = "Three message-passing layers, hidden size 44, 4 heads, focal loss, Adam (Methods 'Strategy 3: GCNN model')"
    configuration(cfg, f"SPOT-MAS tissue-of-origin {mname} ({m})", M["spotmas-too"], [S_NGU, S_NGU_T], m, ver,
                  f"Supplementary file 1 Table S9 header; Methods 'Construction of models for TOO' (P49-P53)", CLIN,
                  mtypes=("supervised_machine_learning",), extra=extra,
                  missing={"version": {"reason": "unreported", "note": "No GCNN software version is given"}} if ver is None else None)
    for blk, (hr, sr, mr, rows) in blocks.items():
        ev = f"{P}-eval-nguyen2023-spotmas-too-{mk}-{blk}"
        evaluation(ev, f"SPOT-MAS tissue of origin, {m} ({blk})", cfg, PR_N[blk], D_N[blk], [S_NGU, S_NGU_T], "author_reported",
                   {"dataset_version": "eLife 12:RP89083", "split": "10-fold cross-validation" if blk == "discovery" else "Independent validation cohort",
                    "population": ("499 cancer patients, five types" if blk == "discovery" else "239 cancer patients, five types"),
                    "inputs": "Nine concatenated SPOT-MAS cfDNA feature sets", "adaptation": None,
                    "metric_implementation": "Correctly assigned patients / patients in the stratum",
                    "aggregation": "Per cancer type and stage stratum", "budget": None},
                   f"Supplementary file 1 Table S9, {m} columns, rows {rows[0]}-{rows[-1]}", CLIN)
        for i, r in enumerate(rows):
            cancer = cancers[i]
            for c, (sk, slab) in strata.items():
                k = models.index(m) + 1
                cell = f"{col_shift(c, k)}{r}"
                raw = s9[cell]
                n_raw = s9[f"{c}{r}"]
                n = int(n_raw)
                stratum = {"all-stage": "all stages", "unknown-stage": "non-metastatic, stage unknown"}.get(sk, slab.replace("Stage", "stage"))
                if cancer == "All cancer":
                    metric, qual = "accuracy", f"tissue of origin, five cancer types; all cancer patients; {stratum}"
                else:
                    metric = "recall"
                    qual = f"tissue of origin, five cancer types; {cancer_name[cancer]} patients (printed as accuracy); {stratum}"
                extra = {"coverage": {"scored": n, "unit": "cancer patients", "note": f"n printed in cell {c}{r}"}}
                miss = None
                if raw == "N/A":
                    miss = {"value": {"reason": "inapplicable", "note": f"Printed N/A; n = {n_raw} in cell {c}{r}"}}
                result(f"{P}-result-nguyen2023-spotmas-too-{mk}-{blk}-{cancer.lower().replace(' ', '-')}-{sk}", ev, [S_NGU, S_NGU_T],
                       f"{N9}, {cell}; {blk.capitalize()} block; row '{cancer}'; column '{m}' under '{slab}' (n in {c}{r})",
                       raw, metric, qual, "fraction", "higher", n_review, extra=extra, missing=miss)
                if m == "RF":
                    # The n column is shared by the three models; listed once, recorded on each result's coverage.
                    claim_rows.append([f"{P}-eval-nguyen2023-spotmas-too-*-{blk}", S_NGU_T,
                                       f"{N9}, {c}{r}; row '{cancer}'; column 'n' under '{slab}'", n_raw, "denominator"])

# ================================================================ relevance judgements
J = f"use-case-mapping-ctdna-methylation-20261009"
CONSTRAINTS = ["Inspect every linked evaluation's source locator and preserved conflicts before citing a result.",
               "Do not combine this mapping's evaluations with any other protocol's results; cohorts, inputs and metrics differ between sources."]


def judgement(short, protocol, relevance, endpoint, rationale, limitations, sources, cites, group, title, metric, label, order):
    rec(f"{J}-{short}", "claim", f"Relevance of {protocol} to \"Select a plasma ctDNA methylation detection workflow\"",
        rationale, sources, [{"relation": "subject", "target_id": UC}],
        {"field": f"links:assessed_by:{protocol}", "value": protocol, "relevance": relevance, "endpoint": endpoint,
         "rationale": rationale, "constraints": CONSTRAINTS, "limitations": limitations,
         "citation_locators": [{"source_id": s, "locator": loc} for s, loc in cites],
         "source_locator": "; ".join(f"{s}: {loc}" for s, loc in cites), "revision": 1,
         "reason": "Add primary-source cfDNA methylation comparison evidence from the plasma ctDNA methylation use-case pass 2026-10-09.",
         "comparison_group": group, "comparison_title": title, "headline_metric": metric,
         "stratum_label": label, "stratum_order": order}, facets={})


SUN_T = "Deconvolution-based cancer detection on real plasma (Sun et al. 2024)"
judgement("sun2024-hcc-wgbs", PR_SUN_HCC, "proxy",
          "ROC-AUC for liver cancer vs healthy plasma (24 vs 32, WGBS) of a random forest on cell-type fractions from CelFEER, CelFiE, cfNOMe, MethAtlas and UXM",
          "Measures plasma cancer detection by methylation deconvolution on real patient samples, but as a discrimination AUC from a downstream random forest rather than sensitivity at a declared specificity.",
          ["24 cases and 32 controls", "Random forest validation split not stated; AUC may be in-sample", "No uncertainty reported",
           "Independent benchmark (no author developed the five tools)"],
          [S_SUN, S_SUN_T], [(S_SUN, "Methods P30, P41; Results P20-P21"), (S_SUN_T, "Table S7 H3:M4")],
          "sun2024-real-plasma-detection", SUN_T, "auroc", "Liver cancer, plasma WGBS", 1)
judgement("sun2024-cfmethyl", PR_SUN_CFM, "proxy",
          "ROC-AUC per cancer type (liver, colon, lung adenocarcinoma, lung squamous, gastric) vs 193 healthy plasma samples (cfMethyl-Seq) of a random forest on cell-type fractions from five deconvolution methods",
          "Measures plasma cancer detection by methylation deconvolution on real patient samples, but as a discrimination AUC from a downstream random forest rather than sensitivity at a declared specificity.",
          ["30 to 67 cases per cancer type against the same 193 controls", "Random forest validation split not stated; AUC may be in-sample",
           "No uncertainty reported", "Cohort is the cfMethyl-Seq study cohort (Stackpole et al. 2022) with different counts from the stored amp-data-cfmethyl-408"],
          [S_SUN, S_SUN_T], [(S_SUN, "Methods P30, P41; Results P20-P21"), (S_SUN_T, "Table S7 H3:M3, H5:M9")],
          "sun2024-real-plasma-detection", SUN_T, "auroc", "Five cancers, plasma cfMethyl-Seq", 2)
G_T = "Tumour-fraction limit of detection in in silico mixtures (DecoNFlow benchmark, Giuili et al. 2025)"
for order, ds in enumerate(("wgbs-tt", "rrbs-tt", "rrbs-cl"), start=1):
    lim = ["In silico mixtures of tumour tissue or cell-line reads into healthy plasma reads, not patient plasma",
           "Medians on a discrete grid of tested fractions", "Preprint, not peer reviewed",
           "Supplementary Table 3 sheet A RRBS-CL block conflicts with sheet B and Figure 4A (source evidence concern)"]
    judgement(f"giuili2025-{ds}", PR_G[ds], "proxy",
              f"Median tumour-fraction limit of detection of ten reference-based deconvolution tools on {datasets[ds][0]} mixtures, by sequencing depth and overall",
              "The limit of detection of tumour-derived DNA in plasma-like mixtures bears on which deconvolution tool detects low tumour fractions, but the mixtures are simulated from tissue or cell-line reads rather than patient plasma.",
              lim, [S_GIU, S_GIU_T3],
              [(S_GIU, "Results 'The tumoral fraction limit of detection', Figure 4, Methods 'Evaluation metrics and missing values'"),
               (S_GIU_T3, "Sheets A and B")],
              "giuili2025-tumour-fraction-lod", G_T, "limit-of-detection", datasets[ds][0], order)
N_T = "Tissue-of-origin classifiers on SPOT-MAS plasma features (Nguyen et al. 2023)"
for order, blk in enumerate(("discovery", "validation"), start=1):
    judgement(f"nguyen2023-too-{blk}", PR_N[blk], "proxy",
              f"Five-class tissue-of-origin accuracy of random forest, deep neural network and graph convolutional network classifiers on SPOT-MAS plasma features ({'discovery cohort, 10-fold cross-validation' if blk == 'discovery' else 'independent validation cohort'}), overall and by cancer type and stage",
              "Measures tissue-of-origin identification from plasma cfDNA, the part of the question allowed where separately supported, but the features combine methylation with fragmentomic and copy-number signals and only cancer patients are classified.",
              TOO_LIM, [S_NGU, S_NGU_T],
              [(S_NGU, "Results P23-P25, Methods P49-P53, Discussion P31"), (S_NGU_T, f"Table S9 rows {blocks[blk][0]}-{blocks[blk][3][-1]}")],
              "nguyen2023-spotmas-too", N_T, "accuracy", "Discovery cohort (10-fold CV)" if blk == "discovery" else "Independent validation cohort", order)

# ---------------------------------------------------------------- write
records.sort(key=lambda r: r["id"])
ids = [r["id"] for r in records]
if len(ids) != len(set(ids)):
    raise SystemExit("Duplicate IDs")
with open(os.path.join(BATCH, "batch.jsonl"), "w") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(BATCH, "claims.csv"), "w", newline="") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    for row in sorted(claim_rows):
        w.writerow(row)
from collections import Counter
print(Counter(r["kind"] for r in records), len(records))
