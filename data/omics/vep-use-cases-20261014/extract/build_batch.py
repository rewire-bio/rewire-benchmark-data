"""Build the vep-use-cases-20261014 batch.

Usage (from the repository root):
  python3 -I data/omics/vep-use-cases-20261014/extract/build_batch.py <download-dir>

<download-dir> holds the retrieved artifacts named as in SOURCES below and in tools.py.
Every artifact is checked against its pinned SHA-256 before use. Writes batch.jsonl,
claims.csv and coverage.json in the batch folder. Deterministic: the same inputs give
the same bytes. Extraction only; every record is needs_review or discovered.
"""
import csv
import gzip
import hashlib
import html
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pmc_html import normalised_sha256  # noqa: E402
from tools import EXCLUDED, GAPS, TOOLS  # noqa: E402

PINS = json.load(open(os.path.join(HERE, "pins.json")))

BATCH = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(BATCH, "..", "..", ".."))
P = "vep-uc-20261014"
TODAY = "2026-10-14"
UC151 = "use-case-missense-pp3-bp4-calibrated-evidence"
UC152 = "use-case-protein-variant-effect-prediction"

COLLECTOR = "Collector agent for the 2026-10-14 VEP use-case pass (Claude Opus 5.5); extraction only, not a review. Pending an independent review-evidence pass."


def review(sha, url, note, method=("ai-assisted-source-review",), method_note="Read by the collector agent from the pinned artifact."):
    return {"method": list(method), "method_note": method_note, "reviewer": ["claude"], "reviewer_note": COLLECTOR,
            "date": TODAY, "artifact_sha256": sha, "retrieval_url": url, "note": note}


# ---------------------------------------------------------------- sources
SOURCES = {
    "pejaver2022": dict(file="pejaver2022.xml", mode="raw", sha="a78c7bcaacb0ccb72291264bbe7c1f9a16867b0c6207dcbb45c3c59a14af6b3b",
                        url="https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9748256/fullTextXML", retrieved_at="2026-10-14T14:44:42Z",
                        name="Pejaver et al. 2022, Am J Hum Genet 109:2163 (Europe PMC full text XML)",
                        description="ClinGen Sequence Variant Interpretation Working Group calibration of 13 missense predictors to ACMG/AMP PP3 and BP4 evidence strengths, with score thresholds per strength and a check of developer-recommended thresholds.",
                        doi="10.1016/j.ajhg.2022.10.013", version="PMC9748256 (Am J Hum Genet 2022;109(12):2163)", licence="CC BY 4.0", status="peer_reviewed",
                        locator="Methods 'Data sets', 'Estimation of the prevalence of pathogenic variants', 'Statistical framework'; Tables 1-4; Declaration of interests; Data and code availability",
                        limitations=["Table S1 (point estimates and one-sided confidence intervals behind Table 2) is in the supplement, which was not retrieved.",
                                     "Thresholds are estimated genome-wide; the Discussion notes that evidence strength can differ between genes."]),
    "bergquist2025": dict(file="bergquist2025.html", mode="pmc_html", sha="4fe954451167b5a5717a4c37f4054432e1f02fb59862d0fb909edb525e6bb8e2",
                          raw_sha="214864e7b556fcd7f8344a328a5b42ab5c334703de96063e130406ebe304c2d4",
                          url="https://pmc.ncbi.nlm.nih.gov/articles/PMC12208618/", retrieved_at="2026-10-14T14:44:51Z",
                          name="Bergquist et al. 2025, Genet Med 27:101402 (PMC author manuscript)",
                          description="Calibration of AlphaMissense, ESM1b and VARITY_R (EVE attempted) for ACMG/AMP PP3 and BP4 with the Pejaver et al. 2022 data and method, and point-based score intervals for BayesDel, MutPred2, REVEL and VEST4.",
                          doi="10.1016/j.gim.2025.101402", version="PMC12208618, NIH author manuscript of Genet Med 2025;27(6):101402", licence="NIH author manuscript in PMC; publisher copyright, no open licence stated", status="peer_reviewed",
                          locator="Abstract; Materials and Methods; Results; Table 1 and caption",
                          limitations=["Author manuscript, not the publisher's version of record.",
                                       "EVE thresholds are given in the text, but the authors do not recommend them because EVE scored only about half of the benign variants (Results); they are not extracted."]),
    "stenton2024": dict(file="stenton2024.html", mode="pmc_html", sha="debe1ae8e304ac0a6272c093bcf7874977e7b9b3921dbe7f5ba096701611ebe7",
                        raw_sha="c39211252470dbf0f2c8f0c43506f0a66fc868c06c34cc5bee56d77fb344037d",
                        url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11560577/", retrieved_at="2026-10-14T14:49:14Z",
                        name="Stenton et al. 2024, Genet Med 26:101213 (PMC author manuscript)",
                        description="Evidence yield of the calibrated PP3/BP4 recommendations in 300 Rare Genomes Project probands, with practical guidance on applying them.",
                        doi="10.1016/j.gim.2024.101213", version="PMC11560577, NIH author manuscript of Genet Med 2024;26(11):101213", licence="NIH author manuscript in PMC; publisher copyright, no open licence stated", status="peer_reviewed",
                        locator="Abstract; Table 1 (guidance); Table 2 (evidence yield per proband)",
                        limitations=["Cited for guidance and limitations only; Table 2 (evidence yield) is not extracted."]),
    "tejura2024": dict(file="tejura2024.html", mode="pmc_html", sha="e00fb418efba3924e47db1aba3be26835dbdbb9f0a4c14aca06a61215ca16ecf",
                       raw_sha="d84ecae985d9c3362e0b83596b7df28a13c8007230389a9a8f48fa9e1ba1178f",
                       url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11393694/", retrieved_at="2026-10-14T14:49:15Z",
                       name="Tejura et al. 2024, Am J Hum Genet 111:2031 (PMC)",
                       description="Gene-by-gene analysis of REVEL and BayesDel ClinGen SVI score intervals in 3,668 disease-relevant genes, showing heterogeneous performance hidden by genome-wide calibration.",
                       doi="10.1016/j.ajhg.2024.07.018", version="PMC11393694 (Am J Hum Genet 2024;111(9):2031)", licence="Not stated on the retrieved page", status="peer_reviewed",
                       locator="Summary",
                       limitations=["Cited for its summary finding only; its tables are not extracted."]),
}

NORMALISED_NOTE = ("artifact_sha256 is the SHA-256 of the retrieved page with the two per-request tokens blanked "
                   "(the content of <meta name=\"ncbi_phid\"> and the csrfmiddlewaretoken value), computed by "
                   "data/omics/vep-use-cases-20261014/extract/pmc_html.py; a re-download hashes the same. "
                   "The raw bytes of the 2026-10-14 retrieval hashed to {raw}.")


def load(downloads, file, mode, sha):
    data = open(os.path.join(downloads, file), "rb").read()
    got = normalised_sha256(data) if mode == "pmc_html" else hashlib.sha256(data).hexdigest()
    if got != sha:
        raise SystemExit(f"{file}: SHA-256 {got} does not match pinned {sha}")
    return data


def source_record(sid, s, extra_desc=None):
    attrs = {"url": s["url"], "version": s["version"], "retrieved_at": s["retrieved_at"], "artifact_sha256": s["sha"],
             "publication_status": s["status"], "licence": s["licence"], "source_locator": s["locator"]}
    if s.get("doi"):
        attrs["doi"] = s["doi"]
    if s["mode"] == "pmc_html":
        attrs["media_type"] = "text/html"
        attrs["hash_scope"] = NORMALISED_NOTE.format(raw=s["raw_sha"])
    else:
        attrs["hash_scope"] = "Exact downloaded bytes, before optional gzip storage"
        attrs["media_type"] = {"xml": "application/xml", "pdf": "application/pdf", "md": "text/markdown", "html": "text/html"}[s["file"].rsplit(".", 1)[1]]
    if s.get("limitations"):
        attrs["limitations"] = s["limitations"]
    if s.get("mutable"):
        attrs["access_note"] = s["mutable"]
    if not s.get("doi"):
        attrs["missing_metadata"] = {"doi": {"reason": "inapplicable", "note": "Repository file pinned to a commit"}}
    attrs["review"] = review(s["sha"], s["url"], "Identity, version, licence and the text used for record descriptions read from the artifact.")
    return {"id": sid, "kind": "source", "name": s["name"], "description": s["description"], "status": "needs_review",
            "facets": {"areas": s.get("areas", ["dna-genomes"]), "contexts": s.get("contexts", ["clinical_research"])},
            "source_ids": [], "links": [], "attributes": attrs}


# ---------------------------------------------------------------- table parsing
def clean(s):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))).strip()


def rows_of(table_xml):
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", table_xml, re.S):
        rows.append([clean(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)])
    return rows


def pejaver_tables(xml):
    t = xml.decode("utf8")
    wraps = {}
    for w in re.findall(r"<table-wrap .*?</table-wrap>", t, re.S):
        label = clean((re.findall(r"<label>(.*?)</label>", w, re.S) or [""])[0])
        wraps[label] = w
    assert set(wraps) == {"Table 1", "Table 2", "Table 3", "Table 4"}, wraps.keys()
    t2 = rows_of(wraps["Table 2"])
    assert t2[0] == ["Method", "Benign (BP4)", "Pathogenic (PP3)"], t2[0]
    assert t2[1] == ["Very Strong", "Strong", "Moderate", "Supporting", "Supporting", "Moderate", "Strong", "Very Strong"], t2[1]
    body2 = t2[2:]
    assert [r[0] for r in body2] == ["BayesDel", "CADD", "EA", "FATHMM", "GERP++", "MPC", "MutPred2", "PhyloP", "PolyPhen2", "PrimateAI", "REVEL", "SIFT", "VEST4"], [r[0] for r in body2]
    assert all(len(r) == 9 for r in body2)
    assert "A “–” implies that the given tool did not meet the posterior probability" in clean(wraps["Table 2"])
    t3 = rows_of(wraps["Table 3"])
    assert t3[0] == ["Method", "Pathogenicity score threshold", "lr +", "Evidence strength", "Fraction of predicted pathogenic variants in the gnomAD set"], t3[0]
    body3 = t3[1:]
    assert [r[0] for r in body3] == ["SIFT", "PolyPhen-2", "CADD"], body3
    return body2, body3


def bergquist_table(page):
    t = page.decode("utf8")
    tables = re.findall(r"<table.*?</table>", t, re.S)
    assert len(tables) == 1
    rows = rows_of(tables[0])
    assert rows[0] == ["Method", "Benign (BP4)", "Indeterminate (0)", "Pathogenic (PP3)"], rows[0]
    assert rows[1] == ["Strong (−4)", "(−3)", "Moderate (−2)", "Supporting (−1)", "Supporting (+1)", "Moderate (+2)", "(+3)", "Strong (+4)"], rows[1]
    body = rows[2:]
    assert [r[0] for r in body] == ["BayesDel", "MutPred2", "REVEL", "VEST4", "AlphaMissense", "ESM1b", "VARITY_R"], [r[0] for r in body]
    assert all(len(r) == 10 for r in body)
    text = clean(re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S))
    cap = text[text.find("Table 1. Estimated threshold intervals"):][:2000]
    assert cap and "All methods calibrated in this study are indicated in bold" in cap
    return body


NUM = r"−?\d+(?:\.\d+)?"


def to_dec(s):
    return s.replace("−", "-")


def parse_cell(cell):
    """Return (kind, bounds) for a printed interval cell."""
    c = cell.replace(" ", "")
    if c in ("–", "-"):
        return "none", []
    m = re.fullmatch(r"(≤|≥)(" + NUM + ")", c)
    if m:
        return m.group(1), [to_dec(m.group(2))]
    m = re.fullmatch(r"([\[(])(" + NUM + "),(" + NUM + r")([\])])", c)
    if m:
        return "interval", [to_dec(m.group(2)), to_dec(m.group(3))]
    if re.fullmatch(NUM, c):
        return "point", [to_dec(c)]
    raise SystemExit(f"unparsed cell {cell!r}")


def threshold(cell, stronger_cell):
    """Bound a score must reach to receive this strength: for a one-sided cell its bound; for an
    interval, the bound further from the next-stronger cell's bound (the inner bound)."""
    kind, b = parse_cell(cell)
    if kind == "none":
        return None
    if kind in ("≤", "≥", "point"):
        return b[0]
    sk, sb = parse_cell(stronger_cell) if stronger_cell is not None else ("none", [])
    if sk == "none":
        raise SystemExit(f"interval {cell} has no stronger neighbour to orient it")
    # the outer end is the one nearest any bound of the stronger cell
    dist = [min(abs(float(x) - float(y)) for y in sb) for x in b]
    if dist[0] == dist[1]:
        raise SystemExit(f"cannot orient {cell} against {stronger_cell}")
    return b[1] if dist[0] < dist[1] else b[0]


# ---------------------------------------------------------------- store lookups
def store_index():
    idx = {}
    for kind in ("methods", "models", "configurations", "protocols", "sources", "use-cases", "datasets"):
        for line in open(os.path.join(REPO, "data", "entities", f"{kind}.jsonl")):
            r = json.loads(line)
            idx[r["id"]] = r
    return idx


def main(downloads):
    idx = store_index()
    recs = []
    claims_rows = []

    # sources for calibration papers
    data = {k: load(downloads, s["file"], s["mode"], s["sha"]) for k, s in SOURCES.items()}
    sid = {k: f"{P}-source-{k}" for k in SOURCES}
    for k, s in SOURCES.items():
        recs.append(source_record(sid[k], s))

    t2, t3 = pejaver_tables(data["pejaver2022"])
    bq = bergquist_table(data["bergquist2025"])

    pej_sha, pej_url = SOURCES["pejaver2022"]["sha"], SOURCES["pejaver2022"]["url"]
    bq_sha, bq_url = SOURCES["bergquist2025"]["sha"], SOURCES["bergquist2025"]["url"]

    # ---------------------------------------------------------- tool records (#153-#155)
    tool_ids = {}
    for t in [t for t in TOOLS if t["slug"] not in EXCLUDED]:
        d = load(downloads, t["file"], t["mode"], PINS[t["slug"]]["sha"])
        sha, raw = PINS[t["slug"]]["sha"], hashlib.sha256(d).hexdigest()
        if t["mode"] == "pmc_html" and raw != PINS[t["slug"]]["raw_sha"]:
            print(f"note: {t['file']} raw bytes differ from the 2026-10-14 retrieval (per-request tokens); normalised hash matches", file=sys.stderr)
        raw = PINS[t["slug"]]["raw_sha"]
        t["sha"], t["raw_sha"] = sha, raw
        src = dict(file=t["file"], mode=t["mode"], sha=sha, raw_sha=raw, url=t["url"], retrieved_at=t["retrieved_at"],
                   name=f"{t['citation']} ({'Europe PMC full text XML' if t['file'].endswith('.xml') else 'PMC article page' if t['mode']=='pmc_html' else 'repository README at commit' if t['file'].endswith('.md') else 'publisher PDF' if t['file'].endswith('.pdf') else 'preprint page'})",
                   description=f"Primary source for {t['name']} (rewire-benchmark-data #{t['issue']}).", doi=t.get("doi"), version=t["version"],
                   licence=t["licence"], status=t["status"], locator="Abstract; availability statements" if not t["file"].endswith(".md") else "README",
                   areas=t["areas"], contexts=["clinical_research"] if t["issue"] != 155 else ["research", "clinical_research"])
        if t["file"].endswith(".html") and t["mode"] == "raw":
            src["mutable"] = "Mutable web page; the hash describes the 2026-10-14 retrieval (two retrievals 2026-10-14 were byte-identical)."
        if t.get("note"):
            src["limitations"] = [t["note"]]
        s_id = f"{P}-source-{t['slug']}"
        recs.append(source_record(s_id, src))
        rid = f"{P}-{t['kind']}-{t['slug']}"
        tool_ids[t["slug"]] = rid
        attrs = {"reported_name": t.get("reported_name", t["name"]), "entity_level": "method" if t["kind"] == "method" else "family",
                 "access": t["access"], "source_locator": t.get("locator", "Abstract; availability statements" if not t["file"].endswith(".md") else "README"),
                 "missing_metadata": {"version": {"reason": "unreported", "note": "The source names no release or version for the tool"}}}
        if t["kind"] == "model":
            attrs["licence"] = t["licence"] if t["file"].endswith(".md") else "Not stated for the model in the captured source"
            if t.get("training_data") and t["training_data"] != "Not extracted":
                attrs["training_data"] = t["training_data"]
            else:
                attrs["missing_metadata"]["training_data"] = {"reason": "unextracted"}
        attrs["review"] = review(sha, t["url"], "Name, description and access transcribed from the source." + (" " + t["note"] if t.get("note") else ""))
        recs.append({"id": rid, "kind": t["kind"], "name": t["name"], "description": t["description"], "status": "discovered",
                     "facets": {"areas": t["areas"], "contexts": ["clinical_research"] if t["issue"] != 155 else ["research", "clinical_research"], "method_types": t["method_types"]},
                     "source_ids": [s_id], "links": [], "attributes": attrs})

    # ---------------------------------------------------------- calibration benchmark, datasets, protocols
    bench = f"{P}-benchmark-clingen-svi-calibration"
    recs.append({"id": bench, "kind": "benchmark", "name": "ClinGen SVI calibration of computational predictors for PP3/BP4",
                 "description": "Local posterior probability calibration of missense predictor scores to ACMG/AMP evidence strengths (PP3 for pathogenicity, BP4 for benignity), on ClinVar missense variants with a prior probability of pathogenicity estimated from gnomAD.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
                 "source_ids": [sid["pejaver2022"], sid["bergquist2025"]], "links": [],
                 "attributes": {"entity_level": "suite", "version": "Pejaver et al. 2022 (13 tools) and Bergquist et al. 2025 (3 further tools, point-based intervals)",
                                "task": "Calibrate predictor score thresholds to ACMG/AMP evidence strengths for missense variants",
                                "scope_note": "Calibration on the ClinVar 2019 set (11,834 missense variants, 1,914 genes, rare in gnomAD, training variants of the tools removed where available); prior probability of pathogenicity 4.41% from the gnomAD set by DistCurve; thresholds where the one-sided 95% bootstrap bound of the local positive likelihood ratio reaches 2.406, 5.790, 33.53 and 1,124 (Supporting to Very Strong).",
                                "source_locator": "Pejaver et al. 2022 Methods and Table 1; Bergquist et al. 2025 Materials and Methods",
                                "limitations": ["Genome-wide calibration; evidence strength varies between genes (Tejura et al. 2024).",
                                                "Several authors of Pejaver et al. 2022 developed calibrated tools: B.-J. Feng (BayesDel; reference 13 is Feng's PERCH paper), V. Pejaver, K.A. Pagel, S.D. Mooney and P. Radivojac (MutPred2, reference 19), V. Pejaver (REVEL, reference 23), R. Karchin (VEST4, reference 25) and A. O'Donnell-Luria (MPC, reference 18)."],
                                "review": review(pej_sha, pej_url, "Scope and limitations from the Methods, Table 1, author list and references.")}})
    ds_cv = f"{P}-dataset-pejaver2022-clinvar2019"
    ds_gn = f"{P}-dataset-pejaver2022-gnomad"
    recs.append({"id": ds_cv, "kind": "dataset", "name": "ClinVar 2019 calibration set (Pejaver et al. 2022)",
                 "description": "ClinVar pathogenic, likely pathogenic, likely benign and benign missense variants used to calibrate predictor scores to ACMG/AMP evidence strengths.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}, "source_ids": [sid["pejaver2022"]], "links": [],
                 "attributes": {"version": "ClinVar VCF downloaded December 2019, filtered as in Figure 1A", "split": "Whole set used for calibration; the ClinVar 2020 set (9,114 variants from 2,197 genes, submitted after December 2019) is the separate test set",
                                "population": "11,834 missense variants from 1,914 genes: allele frequency below 0.01 in gnomAD v2.1, genes with at least one pathogenic variant of any type in ClinVar, VUS, zero-star and conflicting entries removed, and variants in the training sets of BayesDel, FATHMM, MPC, MutPred2, PolyPhen-2, REVEL and VEST4 (and constituent tools of the meta-predictors) removed where available.",
                                "label_semantics": "Positive: ClinVar pathogenic or likely pathogenic. Negative: ClinVar benign or likely benign.",
                                "species": "Homo sapiens", "access": "Supplementary Data S1 (Excel), not retrieved in this pass.",
                                "source_locator": "Methods 'Data sets: The ClinVar 2019 set'; Figure 1A; Data and code availability",
                                "review": review(pej_sha, pej_url, "Counts and filters from the Methods.")}})
    recs.append({"id": ds_gn, "kind": "dataset", "name": "gnomAD reference set (Pejaver et al. 2022)",
                 "description": "Rare gnomAD missense variants in genes with at least one ClinVar pathogenic variant, used to estimate the prior probability of pathogenicity (4.41%) and to count how often each evidence strength is assigned.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}, "source_ids": [sid["pejaver2022"]], "links": [],
                 "attributes": {"version": "gnomAD v2.1 exomes and genomes, filtered as in Figure 1B", "split": "Whole set; not a labelled test set",
                                "population": "363,894 variants from 3,640 genes after quality, segmental-duplication and training-set filters and removal of variants in ClinVar (December 2019).",
                                "label_semantics": "Unlabelled reference population; used for the prior and for the fraction of variants assigned each strength.",
                                "species": "Homo sapiens", "access": "Supplementary Data S2 (Excel), not retrieved in this pass.",
                                "source_locator": "Methods 'The gnomAD set' and 'Estimation of the prevalence of pathogenic variants'; Figure 1B",
                                "review": review(pej_sha, pej_url, "Counts and filters from the Methods.")}})

    metric_impl = ("Local posterior probability of pathogenicity estimated in a sliding score window on the ClinVar 2019 set with prior 0.0441; "
                   "a threshold is the most lenient score at which the one-sided 95% bootstrap bound (10,000 iterations) of the local positive likelihood ratio still reaches the cut-off for that strength (2.406, 5.790, 33.53, 1,124; reciprocals for BP4)")
    pr_int = f"{P}-protocol-pejaver2022-intervals"
    pr_lr = f"{P}-protocol-pejaver2022-developer-threshold-lr"
    pr_fr = f"{P}-protocol-pejaver2022-developer-threshold-gnomad-fraction"
    pr_bq = f"{P}-protocol-bergquist2025-point-intervals"
    common_lims = ["Calibration is genome-wide (average over genes); Tejura et al. 2024 report that about 70% of the gene-level REVEL and BayesDel intervals with enough control variants exceeded the number of incorrect predictions the genome-wide recommendations imply.",
                   "Labels are ClinVar classifications; the authors assume computational evidence had no major role in them (Stenton et al. 2024, Table 1).",
                   "Developers of BayesDel, MPC, MutPred2, REVEL and VEST4 are authors of Pejaver et al. 2022 (see the benchmark record)."]
    recs.append({"id": pr_int, "kind": "protocol", "name": "PP3/BP4 score intervals per evidence strength (Pejaver et al. 2022 Table 2)",
                 "description": "Score interval of each of 13 missense predictors for four BP4 and four PP3 evidence strengths, from the ClinGen SVI calibration.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
                 "source_ids": [sid["pejaver2022"]], "links": [{"relation": "part_of", "target_id": bench}, {"relation": "uses_data", "target_id": ds_cv}],
                 "attributes": {"protocol": "Calibrate each tool's scores on the ClinVar 2019 set and report the score interval that reaches each of Supporting, Moderate, Strong and Very Strong for BP4 and PP3; '–' where the strength is not reached.",
                                "task": "Calibrated PP3/BP4 score thresholds", "metric": "evidence-strength-score-interval", "metric_direction": "unknown", "unit": "unitless",
                                "metric_implementation": metric_impl, "version": "Pejaver et al. 2022, Table 2", "publication_status": "peer_reviewed", "denominator": 11834,
                                "source_locator": "Table 2 and footnote; Methods 'Statistical framework' and 'Estimation of thresholds'",
                                "limitations": common_lims + ["Intervals follow mathematical notation: '(' and ')' exclude the end value, '[' and ']' include it (Table 2 footnote).",
                                                              "Point estimates and confidence bounds per threshold are in Table S1, not retrieved."],
                                "review": review(pej_sha, pej_url, "Protocol fields from Table 2, its footnote and the Methods.")}})
    recs.append({"id": pr_lr, "kind": "protocol", "name": "Local likelihood ratio at developer-recommended thresholds (Pejaver et al. 2022 Table 3)",
                 "description": "Local positive likelihood ratio, from the ClinVar 2019 posterior curves, at the default thresholds of SIFT, PolyPhen-2 and CADD, judged against the PP3 Supporting cut-off.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
                 "source_ids": [sid["pejaver2022"]], "links": [{"relation": "part_of", "target_id": bench}, {"relation": "uses_data", "target_id": ds_cv}],
                 "attributes": {"protocol": "Read the local positive likelihood ratio at each tool's developer-recommended pathogenicity threshold and compare it with 2.406 (PP3 Supporting).",
                                "task": "Evidence strength of developer thresholds", "metric": "likelihood-ratio", "metric_direction": "higher", "unit": "unitless",
                                "metric_implementation": "Local positive likelihood ratio at the threshold with 95% bootstrap confidence interval", "version": "Pejaver et al. 2022, Table 3",
                                "publication_status": "peer_reviewed", "source_locator": "Table 3 and footnote; Results 'Investigation of commonly used developer-recommended thresholds'",
                                "limitations": common_lims[:2] + ["Evidence strength was judged on the point estimate of the likelihood ratio (Table 3 footnote)."],
                                "review": review(pej_sha, pej_url, "Protocol fields from Table 3 and the Results.")}})
    recs.append({"id": pr_fr, "kind": "protocol", "name": "Share of gnomAD variants called pathogenic at developer thresholds (Pejaver et al. 2022 Table 3)",
                 "description": "Fraction of the gnomAD reference set that SIFT, PolyPhen-2 and CADD call pathogenic at their default thresholds, against a prior probability of pathogenicity of 4.41%.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
                 "source_ids": [sid["pejaver2022"]], "links": [{"relation": "part_of", "target_id": bench}, {"relation": "uses_data", "target_id": ds_gn}],
                 "attributes": {"protocol": "Count the fraction of gnomAD-set variants at or beyond each tool's developer-recommended pathogenicity threshold.",
                                "task": "Over-calling at developer thresholds", "metric": "proportion", "metric_direction": "lower", "unit": "fraction",
                                "metric_qualifier": "gnomAD-set variants predicted pathogenic at the developer threshold",
                                "version": "Pejaver et al. 2022, Table 3", "publication_status": "peer_reviewed", "denominator": 363894,
                                "source_locator": "Table 3, last column; Results 'Investigation of commonly used developer-recommended thresholds'",
                                "limitations": ["The gnomAD set is unlabelled; a fraction above the 4.41% prior suggests, but does not measure, false positive calls (Results).",
                                                "Lower is treated as better only in relation to the prior; it is not an accuracy."],
                                "review": review(pej_sha, pej_url, "Protocol fields from Table 3 and the Results.")}})
    recs.append({"id": pr_bq, "kind": "protocol", "name": "PP3/BP4 score intervals on the points scale (Bergquist et al. 2025 Table 1)",
                 "description": "Score interval of seven missense predictors for each point value from −4 to +4 of the ACMG/AMP points-based system, including the 3-point level and the indeterminate range.",
                 "status": "needs_review", "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]},
                 "source_ids": [sid["bergquist2025"], sid["pejaver2022"]], "links": [{"relation": "part_of", "target_id": bench}, {"relation": "uses_data", "target_id": ds_cv}],
                 "attributes": {"protocol": "Same data and calibration as Pejaver et al. 2022; report the score interval for Strong (±4), the 3-point level, Moderate (±2), Supporting (±1) and Indeterminate (0). Very Strong was never reached and is not shown.",
                                "task": "Calibrated PP3/BP4 score thresholds", "metric": "evidence-strength-score-interval", "metric_direction": "unknown", "unit": "unitless",
                                "metric_implementation": metric_impl, "version": "Bergquist et al. 2025, Table 1", "publication_status": "peer_reviewed", "denominator": 11834,
                                "source_locator": "Table 1 and caption; Materials and Methods",
                                "limitations": common_lims[:2] + [
                                    "AlphaMissense, ESM1b and VARITY_R are calibrated in this paper; the BayesDel, MutPred2, REVEL and VEST4 rows keep the thresholds of Pejaver et al. 2022 and add the 3-point and indeterminate intervals (caption).",
                                    "V. Pejaver and P. Radivojac (MutPred2; Pejaver also REVEL) are authors.",
                                    "No training-set filtering was done for the new tools: only VARITY was trained on ClinVar, and its precomputed score for each variant comes from a model that excluded that variant (Materials and Methods).",
                                    "The developer thresholds of AlphaMissense (0.564) and ESM1b (−7.5) do not reach Supporting for PP3 or BP4 under this calibration (Results)."],
                                "review": review(bq_sha, bq_url, "Protocol fields from Table 1, its caption and the Materials and Methods.")}})

    # ---------------------------------------------------------- configurations
    TOOL_METHOD = {"BayesDel": "uc-clinical-20260930-method-bayesdel", "CADD": "somatic-oncogenicity-20261009-method-cadd", "EA": tool_ids["ea"],
                   "FATHMM": "somatic-oncogenicity-20261009-method-fathmm", "GERP++": "somatic-oncogenicity-20261009-method-gerp",
                   "MPC": "somatic-oncogenicity-20261009-method-mpc", "MutPred2": "somatic-oncogenicity-20261009-method-mutpred",
                   "PhyloP": "somatic-oncogenicity-20261009-method-phylop", "PolyPhen2": "somatic-oncogenicity-20261009-method-polyphen2",
                   "PrimateAI": "somatic-oncogenicity-20261009-method-primateai", "REVEL": "somatic-oncogenicity-20261009-method-revel",
                   "SIFT": "somatic-oncogenicity-20261009-method-sift", "VEST4": "somatic-oncogenicity-20261009-method-vest4",
                   "AlphaMissense": "somatic-oncogenicity-20261009-method-alphamissense", "ESM1b": "uc20260930-model-esm-1b",
                   "VARITY_R": "somatic-oncogenicity-20261009-method-varity"}
    for name, target in TOOL_METHOD.items():
        if target not in idx and target != tool_ids["ea"]:
            raise SystemExit(f"missing store record {target}")
    slug = lambda n: {"GERP++": "gerp", "PolyPhen2": "polyphen2", "VARITY_R": "varity-r"}.get(n, n.lower())
    PEJ_VERSION = {"BayesDel": "BayesDel without minor allele frequency (scores generated by the authors; release not stated)",
                   "PolyPhen2": "PolyPhen-2 HumVar model (scores generated by the authors; release not stated)",
                   "CADD": "Scores generated by the authors; CADD release not stated", "EA": "Scores generated by the authors; release not stated",
                   "MutPred2": "MutPred2 (scores generated by the authors; release not stated)"}
    DEVELOPER = {"BayesDel": "B.-J. Feng", "MPC": "A. O'Donnell-Luria", "MutPred2": "V. Pejaver, K.A. Pagel, S.D. Mooney and P. Radivojac", "REVEL": "V. Pejaver", "VEST4": "R. Karchin"}
    config = {}
    for row in t2:
        n = row[0]
        cid = f"{P}-config-pejaver2022-{slug(n)}"
        config[n] = cid
        target = TOOL_METHOD[n]
        mt = (idx.get(target) or {}).get("facets", {}).get("method_types") or ["specialist"]
        a = {"reported_name": n, "configuration_type": "paper_evaluation", "foundation_model_eligible": False,
             "version": PEJ_VERSION.get(n, "Precomputed scores from dbNSFP (version not stated in the main text; reference 26 is dbNSFP v4)"),
             "access_reuse": "Scores obtained by Pejaver et al. 2022 (Methods 'Tools'); calibration code at https://github.com/vpejaver/clingen-svi-comp_calibration",
             "score_training_overlap": ("Variants in this tool's training set (and its constituents') were removed from the calibration data where available (Methods)" if n in ("BayesDel", "FATHMM", "MPC", "MutPred2", "PolyPhen2", "REVEL", "VEST4") else "No training-set removal stated for this tool (Methods lists BayesDel, FATHMM, MPC, MutPred2, PolyPhen-2, REVEL and VEST4)"),
             "source_locator": f"Methods 'Tools' and 'Data sets'; Table 2 row '{n}'",
             "review": review(pej_sha, pej_url, "Identity and score source from the Methods.")}
        if n in ("FATHMM", "SIFT"):
            a["parameters"] = "The authors transformed this tool's output so that higher scores indicate pathogenicity (Methods 'Tools'); results keep the Table 2 values as printed"
        recs.append({"id": cid, "kind": "configuration", "name": f"{'PolyPhen-2' if n == 'PolyPhen2' else n} (Pejaver et al. 2022 calibration)",
                     "description": f"{n} scores as calibrated by the ClinGen SVI Working Group in Pejaver et al. 2022.", "status": "needs_review",
                     "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"], "method_types": mt},
                     "source_ids": [sid["pejaver2022"]], "links": [{"relation": "configuration_of", "target_id": target}], "attributes": a})
    BQ_VERSION = {"AlphaMissense": "Precomputed AlphaMissense scores, mapped to the calibration variants by the authors' protocol (Supplementary Materials and Methods, not retrieved); release not stated in the main text",
                  "ESM1b": "Precomputed ESM1b scores (log-likelihood ratio scale), mapped by the authors' protocol; release not stated in the main text",
                  "VARITY_R": "VARITY_R, the model trained on rare variants only; precomputed scores from a model version that excluded each scored variant (Materials and Methods)"}
    for n in ("AlphaMissense", "ESM1b", "VARITY_R"):
        cid = f"{P}-config-bergquist2025-{slug(n)}"
        config[n] = cid
        target = TOOL_METHOD[n]
        mt = idx[target]["facets"].get("method_types") or (["foundation_model"] if n == "ESM1b" else ["supervised_machine_learning"])
        recs.append({"id": cid, "kind": "configuration", "name": f"{n} (Bergquist et al. 2025 calibration)",
                     "description": f"{n} precomputed scores as calibrated for PP3/BP4 in Bergquist et al. 2025.", "status": "needs_review",
                     "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"], "method_types": mt},
                     "source_ids": [sid["bergquist2025"]], "links": [{"relation": "configuration_of", "target_id": target}],
                     "attributes": {"reported_name": n, "configuration_type": "paper_evaluation", "foundation_model_eligible": n == "ESM1b", "version": BQ_VERSION[n],
                                    "access_reuse": "Precomputed scores are freely and publicly available for all possible variants (Materials and Methods)",
                                    "score_training_overlap": "Only VARITY was explicitly trained on ClinVar; no extra filtering against training data was done (Materials and Methods)",
                                    "source_locator": "Materials and Methods 'Selection of computational tools and data preparation'; Table 1",
                                    "review": review(bq_sha, bq_url, "Identity and score source from the Materials and Methods.")}})

    # ---------------------------------------------------------- evaluations and results
    def evaluation(eid, name, cfg, prot, data_id, origin, src_ids, comp, locator, rv, extra=None):
        a = {"origin": origin, "protocol": prot, "comparison": comp, "source_locator": locator,
             "missing_metadata": {"comparison.budget": {"reason": "inapplicable", "note": "Calibration of precomputed scores; no compute budget"}}, "review": rv}
        if extra:
            a.update(extra)
        return {"id": eid, "kind": "evaluation", "name": name, "description": "Published calibration; transcribed, not reproduced.", "status": "needs_review",
                "facets": {"areas": ["dna-genomes"], "contexts": ["clinical_research"]}, "source_ids": src_ids,
                "links": [{"relation": "system", "target_id": cfg}, {"relation": "assessment", "target_id": prot}, {"relation": "data", "target_id": data_id}], "attributes": a}

    def origin_for(n, devs):
        return "author_reported" if n in devs else "independent_paper"

    PEJ_COMP = {"dataset_version": "ClinVar December 2019, filtered (Figure 1A)", "split": "Whole calibration set",
                "population": "11,834 missense variants from 1,914 genes; prior probability of pathogenicity 4.41% (gnomAD set)",
                "inputs": "Precomputed or author-generated scores of the tool for each variant", "adaptation": "None; thresholds fitted to the tool's scores",
                "metric_implementation": metric_impl, "aggregation": "Pooled over variants in all genes", "budget": None}
    STRENGTHS = ["Very Strong", "Strong", "Moderate", "Supporting"]
    for row in t2:
        n = row[0]
        eid = f"{P}-eval-pejaver2022-intervals-{slug(n)}"
        origin = origin_for(n, DEVELOPER)
        extra = {"evidence_overlap": f"Developer overlap: {DEVELOPER[n]}, an author of Pejaver et al. 2022, developed this tool."} if n in DEVELOPER else None
        recs.append(evaluation(eid, f"{n}: PP3/BP4 score intervals (Pejaver et al. 2022)", config[n], pr_int, ds_cv, origin, [sid["pejaver2022"]],
                               dict(PEJ_COMP, protocol_id=pr_int), f"Table 2, row '{n}'",
                               review(pej_sha, pej_url, "Links and comparison fields from the Methods; origin from the author list and references (13, 18, 19, 23, 25)."), extra))
        cells = row[1:]
        cols = [("BP4", s) for s in STRENGTHS] + [("PP3", s) for s in reversed(STRENGTHS)]
        for i, (crit, strength) in enumerate(cols):
            cell = cells[i]
            # next stronger interval: BP4 columns run strongest first, PP3 columns weakest first
            j = i - 1 if crit == "BP4" else i + 1
            stronger = cells[j] if 0 <= j < len(cells) and cols[j][0] == crit else None
            kind, _ = parse_cell(cell)
            num = threshold(cell, stronger) if kind != "none" else None
            rid = f"{P}-result-pejaver2022-{slug(n)}-{crit.lower()}-{strength.lower().replace(' ', '-')}"
            col_label = f"{'Benign (BP4)' if crit == 'BP4' else 'Pathogenic (PP3)'}: {strength}"
            a = {"metric": "evidence-strength-score-interval", "metric_direction": "unknown", "unit": "unitless", "unit_detail": f"{n} score",
                 "metric_qualifier": f"{crit} {strength}, ClinGen SVI calibration (Pejaver et al. 2022)", "printed_value": cell, "numeric_value": num,
                 "source_locator": f"Table 2, row '{n}', column '{col_label}'",
                 "review": review(pej_sha, pej_url, "Extracted by extract/build_batch.py from the pinned JATS XML table-wrap 'Table 2'; header rows, 13 row labels and footnote asserted. Pending independent review.",
                                  method=("deterministic-table-parse",), method_note="Parsed the table-wrap in the pinned XML with header and row labels asserted.")}
            if num is None:
                a["undefined_reason"] = "Not reached: '–' means the tool did not meet the posterior probability (likelihood ratio) threshold for this strength (Table 2 footnote)"
                a["missing_metadata"] = {"uncertainty": {"reason": "inapplicable", "note": "Strength not reached"}}
            else:
                a["numeric_representation"] = ("numeric_value is the printed bound" if kind in ("≤", "≥", "point") else
                                                "numeric_value is the bound a score must reach for this strength: the interval end further from the next-stronger interval")
                a["missing_metadata"] = {"uncertainty": {"reason": "unextracted", "note": "One-sided confidence intervals are in Table S1, not retrieved"}}
            recs.append({"id": rid, "kind": "result", "name": f"{n} {crit} {strength} interval", "description": "Reported value transcribed from the pinned source. Not independently reproduced.",
                         "status": "needs_review", "facets": {}, "source_ids": [sid["pejaver2022"]], "links": [{"relation": "evaluation", "target_id": eid}], "attributes": a})
            claims_rows.append([rid, sid["pejaver2022"], a["source_locator"], cell, "result"])

    for row in t3:
        n = {"PolyPhen-2": "PolyPhen2"}.get(row[0], row[0])
        thr, lr_cell, strength, frac = row[1], row[2], row[3], row[4]
        m = re.fullmatch(r"(\d+\.\d+) \((\d+\.\d+), (\d+\.\d+)\)", lr_cell)
        assert m, lr_cell
        assert strength == "not met"
        for kind_, prot, data_id, eid_part in (("lr", pr_lr, ds_cv, "devlr"), ("fraction", pr_fr, ds_gn, "devfraction")):
            eid = f"{P}-eval-pejaver2022-{eid_part}-{slug(n)}"
            comp = dict(PEJ_COMP, protocol_id=prot, adaptation=f"Developer-recommended pathogenicity threshold {thr} (Table 3)")
            if kind_ == "fraction":
                comp.update(dataset_version="gnomAD v2.1, filtered (Figure 1B)", split="Whole reference set",
                            population="363,894 rare missense variants from 3,640 genes", metric_implementation="Fraction of variants at or beyond the threshold",
                            aggregation="Pooled over variants in all genes")
            else:
                comp.update(metric_implementation="Local positive likelihood ratio at the threshold from the ClinVar 2019 posterior curve; 95% bootstrap interval")
            recs.append(evaluation(eid, f"{row[0]} at developer threshold {thr}: {'local likelihood ratio' if kind_ == 'lr' else 'gnomAD fraction called pathogenic'} (Pejaver et al. 2022)",
                                   config[n], prot, data_id, "independent_paper", [sid["pejaver2022"]], comp, f"Table 3, row '{row[0]}'",
                                   review(pej_sha, pej_url, "Links and comparison fields from Table 3 and the Results.")))
            rid = f"{P}-result-pejaver2022-{eid_part}-{slug(n)}"
            rv = review(pej_sha, pej_url, "Extracted by extract/build_batch.py from table-wrap 'Table 3'; header and row labels asserted. Pending independent review.",
                        method=("deterministic-table-parse",), method_note="Parsed the table-wrap in the pinned XML with header and row labels asserted.")
            if kind_ == "lr":
                a = {"metric": "likelihood-ratio", "metric_direction": "higher", "unit": "unitless",
                     "metric_qualifier": f"local positive likelihood ratio at the developer threshold ({thr}), PP3 Supporting requires 2.406",
                     "printed_value": m.group(1), "numeric_value": m.group(1), "printed_source_cell": lr_cell,
                     "uncertainty": {"type": "confidence_interval", "level": 0.95, "lower": m.group(2), "upper": m.group(3), "printed": f"({m.group(2)}, {m.group(3)})", "method": "bootstrap", "note": "Calculated by the bootstrapping method (Table 3 footnote)"},
                     "criterion": f"Evidence strength column: '{strength}'", "source_locator": f"Table 3, row '{row[0]}', column 'lr +'", "review": rv}
            else:
                a = {"metric": "proportion", "metric_direction": "lower", "unit": "fraction",
                     "metric_qualifier": "gnomAD-set variants predicted pathogenic at the developer threshold",
                     "printed_value": frac, "numeric_value": frac, "denominator": 363894,
                     "source_locator": f"Table 3, row '{row[0]}', column 'Fraction of predicted pathogenic variants in the gnomAD set'",
                     "missing_metadata": {"uncertainty": {"reason": "unreported"}}, "review": rv}
            recs.append({"id": rid, "kind": "result", "name": f"{row[0]} {'lr+' if kind_ == 'lr' else 'gnomAD fraction'} at threshold {thr}",
                         "description": "Reported value transcribed from the pinned source. Not independently reproduced.", "status": "needs_review", "facets": {},
                         "source_ids": [sid["pejaver2022"]], "links": [{"relation": "evaluation", "target_id": eid}], "attributes": a})
            claims_rows.append([rid, sid["pejaver2022"], a["source_locator"], a["printed_value"], "result"])

    BQ_COLS = [("BP4", "Strong", "minus4", "Strong (−4)"), ("BP4", "3 points", "minus3", "(−3)"), ("BP4", "Moderate", "minus2", "Moderate (−2)"),
               ("BP4", "Supporting", "minus1", "Supporting (−1)"), ("Indeterminate", "0 points", "indeterminate", "Indeterminate (0)"),
               ("PP3", "Supporting", "plus1", "Supporting (+1)"), ("PP3", "Moderate", "plus2", "Moderate (+2)"), ("PP3", "3 points", "plus3", "(+3)"),
               ("PP3", "Strong", "plus4", "Strong (+4)")]
    BQ_DEV = {"MutPred2": "V. Pejaver and P. Radivojac", "REVEL": "V. Pejaver"}
    for row in bq:
        n = row[0]
        eid = f"{P}-eval-bergquist2025-intervals-{slug(n)}"
        new = n in ("AlphaMissense", "ESM1b", "VARITY_R")
        extra = {"evidence_overlap": f"Developer overlap: {BQ_DEV[n]}, an author of Bergquist et al. 2025, co-developed this tool."} if n in BQ_DEV else {}
        if not new:
            extra["interpretation"] = "Supporting, Moderate and Strong thresholds are those of Pejaver et al. 2022; the 3-point and indeterminate intervals are added here (Table 1 caption)."
        comp = dict(PEJ_COMP, protocol_id=pr_bq)
        recs.append(evaluation(eid, f"{n}: points-scale PP3/BP4 score intervals (Bergquist et al. 2025)", config[n], pr_bq, ds_cv, origin_for(n, BQ_DEV),
                               [sid["bergquist2025"]] + ([] if new else [sid["pejaver2022"]]), comp, f"Table 1, row '{n}'",
                               review(bq_sha, bq_url, "Links and comparison fields from the Materials and Methods; origin from the author list."), extra or None))
        cells = row[1:]
        for i, (crit, strength, key, header) in enumerate(BQ_COLS):
            cell = cells[i]
            kind, _ = parse_cell(cell)
            if crit == "Indeterminate":
                num, rep = None, "Indeterminate range; no threshold applies"
            elif kind == "none":
                num, rep = None, None
            else:
                j = i - 1 if crit == "BP4" else i + 1
                stronger = cells[j] if 0 <= j < len(cells) and BQ_COLS[j][0] == crit else None
                num = threshold(cell, stronger)
                rep = ("numeric_value is the printed bound" if kind in ("≤", "≥", "point") else
                       "numeric_value is the bound a score must reach for this strength: the interval end further from the next-stronger interval")
            rid = f"{P}-result-bergquist2025-{slug(n)}-{key}"
            a = {"metric": "evidence-strength-score-interval", "metric_direction": "unknown", "unit": "unitless", "unit_detail": f"{n} score",
                 "metric_qualifier": (f"{crit} {strength}" if crit != "Indeterminate" else "Indeterminate (0 points)") + ", ClinGen SVI calibration, points scale (Bergquist et al. 2025)",
                 "printed_value": cell, "numeric_value": num, "source_locator": f"Table 1, row '{n}', column '{header}'",
                 "review": review(bq_sha, bq_url, "Extracted by extract/build_batch.py from the single table on the pinned PMC page; header rows and seven row labels asserted. Pending independent review.",
                                  method=("deterministic-table-parse",), method_note="Parsed the HTML table with header and row labels asserted.")}
            if rep:
                a["numeric_representation"] = rep
            if kind == "none":
                a["undefined_reason"] = "Not reached: '-' means the tool did not meet the likelihood ratio threshold for this strength (Table 1 caption)"
                a["missing_metadata"] = {"uncertainty": {"reason": "inapplicable", "note": "Strength not reached"}}
            else:
                a["missing_metadata"] = {"uncertainty": {"reason": "unreported"}}
            recs.append({"id": rid, "kind": "result", "name": f"{n} {header} interval", "description": "Reported value transcribed from the pinned source. Not independently reproduced.",
                         "status": "needs_review", "facets": {}, "source_ids": [sid["bergquist2025"]], "links": [{"relation": "evaluation", "target_id": eid}], "attributes": a})
            claims_rows.append([rid, sid["bergquist2025"], a["source_locator"], cell, "result"])

    # ---------------------------------------------------------- use cases, baselines and judgements
    from use_cases import use_case_records  # noqa: E402
    uc_recs = use_case_records(P, sid, tool_ids, {"intervals": pr_int, "lr": pr_lr, "fraction": pr_fr, "bergquist": pr_bq}, idx)
    recs.extend(uc_recs)
    for r in uc_recs:
        if r["kind"] == "claim":
            claims_rows.append([r["id"], r["source_ids"][0], r["attributes"].get("source_locator", ""), r["attributes"]["value"], "claim"])

    # ---------------------------------------------------------- write
    ids = [r["id"] for r in recs]
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, dup
    clash = [i for i in ids if i in idx]
    assert not clash, clash
    recs.sort(key=lambda r: r["id"])
    with open(os.path.join(BATCH, "batch.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    with open(os.path.join(BATCH, "claims.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
        for row in sorted(claims_rows):
            w.writerow(row)
    counts = {}
    for r in recs:
        counts[r["kind"]] = counts.get(r["kind"], 0) + 1
    print(json.dumps(counts, sort_keys=True))
    return recs


if __name__ == "__main__":
    main(sys.argv[1])
