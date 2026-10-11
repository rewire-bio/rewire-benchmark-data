"""Dorney et al. 2026 (bioRxiv 10.64898/2026.08.07.743439 v1): long-read fusion caller benchmark.

Extracts every cell of the authors' repository tables Figures/Input_dataframes/stat_summary.tsv (simulated
fusions) and counts_SGNex_summary.tsv.gz (known and other calls on SG-NEx K562 and MCF7), and the three
Huh7 known-fusion recovery counts printed in Results.

Usage: python3 -I extract_fusion_longread.py <preprint.xml> <repo-folder> <batch-folder>
<repo-folder> holds the repository files at the pinned commit, under their repository paths.
"""
import sys, os, re, html, json, gzip, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, read_tsv, FUSION_UC

xml, repo, folder = sys.argv[1:4]
XML_SHA = sha256(xml)
assert XML_SHA == "c665bb407799324bc50ae1792d82574a41ae4a9182befd360973d89a82cbaa5b", XML_SHA
COMMIT = "83e629fed3098881079fd9ac1c8bc13478ce69ed"
FILES = ["Figures/Input_dataframes/stat_summary.tsv", "Figures/Input_dataframes/counts_SGNex_summary.tsv.gz",
         "Fusions/runtools/Run_GFSLGF.sh", "Fusions/runtools/RunJAFFAL.sh", "Fusions/runtools/RunCTAT-LR-fusion.sh", "Fusions/runtools/RunGFSeeker.sh",
         "SimulatedData/Data_Analysis_Scripts/Precision_Recall_ReadSupp_stats.R", "CellLineData/SGNex_DiscoveryNRecall.R"]
bundle = {"repository": "https://github.com/RDorney/LRFusionBenchmark", "commit": COMMIT, "files": []}
for p in FILES:
    raw = open(os.path.join(repo, p), "rb").read()
    entry = {"path": p, "sha256": hashlib.sha256(raw).hexdigest()}
    if p.endswith(".gz"):
        entry["content_gunzipped"] = gzip.decompress(raw).decode()
    else:
        entry["content"] = raw.decode()
    bundle["files"].append(entry)
blob = json.dumps(bundle, indent=1, sort_keys=True).encode() + b"\n"
os.makedirs(os.path.join(folder, "artifacts"), exist_ok=True)
BUNDLE_SHA = hashlib.sha256(blob).hexdigest()
for name, data in (("lrfusionbenchmark-bundle.json.gz", blob), ("preprint-v1.xml.gz", open(xml, "rb").read())):
    with open(os.path.join(folder, "artifacts", name), "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as g:
            g.write(data)

stat = read_tsv(os.path.join(repo, FILES[0]))
counts = read_tsv(os.path.join(repo, FILES[1]))
assert list(stat[0].keys()) == ["control", "depth", "Sequence_Identity", "Algorithm", "False_Point", "True_Point", "Spiked_Number", "FDR", "Precision", "Recall", "F1", "Sensitivity"]
assert len(stat) == 50 and {r["control"] for r in stat} == {"positive"}
assert list(counts[0].keys()) == ["Source", "Cell_Lines", "Sequencing_Depth", "Algorithm", "Library", "knownnumber", "novelnumber"]
assert len(counts) == 172
CALLERS = ["CTAT-LR-Fusion", "FusionSeeker", "GFSeeker", "Genion", "JAFFAL", "LongGF"]
assert sorted({r["Algorithm"] for r in stat}) == CALLERS and sorted({r["Algorithm"] for r in counts}) == CALLERS
for r in stat:
    assert r["Recall"] == r["Sensitivity"], r  # the Sensitivity column duplicates Recall
body = html.unescape(re.sub(r"<[^>]+>", "", open(xml, encoding="utf-8").read()))
HUH7 = "Of the 34 previously reported Huh7 fusion transcripts, 21 were recovered across the evaluated sequencing libraries. PacBio Kinnex recovered the greatest number of known fusions (20), followed by ONT PCR-cDNA (17), whereas Illumina recovered 15."
assert HUH7 in re.sub(r"\s+", " ", body)

XURL = "https://www.biorxiv.org/content/early/2026/08/12/2026.08.07.743439.source.xml"
RURL = f"https://github.com/RDorney/LRFusionBenchmark/tree/{COMMIT}"
b = Batch(folder, "rna-fusion-longread-20261011", ["rna-transcriptomes"])
DESC = "Primary source retrieved and hashed for the 2026-10-11 oncology use-case literature pass."
PRE = b.source("rna-fusion-longread-20261011-source-dorney2026", "A comprehensive benchmark of transcriptome-wide fusion detection using long-read RNA sequencing", {
    "url": "https://doi.org/10.64898/2026.08.07.743439", "artifact_url": XURL, "version": "bioRxiv preprint version 1, posted 2026-08-12; JATS XML",
    "retrieved_at": "2026-10-11T21:36:20Z", "artifact_sha256": XML_SHA, "doi": "10.64898/2026.08.07.743439", "publication_status": "preprint",
    "licence": "CC-BY-4.0", "media_type": "application/xml"}, DESC)
REPO = b.source("rna-fusion-longread-20261011-source-dorney2026-repository", "LRFusionBenchmark repository (Dorney et al.): result tables and run scripts", {
    "url": "https://github.com/RDorney/LRFusionBenchmark", "artifact_url": RURL,
    "version": f"Git commit {COMMIT} (pushed 2026-08-25); files: " + ", ".join(FILES),
    "retrieved_at": "2026-10-11T21:48:03Z", "artifact_sha256": BUNDLE_SHA, "publication_status": "official_project_source", "licence": "MIT",
    "hash_scope": "SHA-256 of a JSON bundle listing each retrieved file with its path, its own SHA-256 and its content (gzipped files decompressed); archived as artifacts/lrfusionbenchmark-bundle.json.gz",
    "media_type": "application/json",
    "limitations": ["The repository is the authors' own; DATA_LICENSES.md releases project-generated data under the MIT licence.",
                    "GitHub repositories are mutable; the commit pins this retrieval."]}, "Authors' official repository, retrieved at a pinned commit and hashed for the 2026-10-11 oncology use-case literature pass.")
SIDS = [PRE, REPO]
def REVIEW(loc, how):
    return extraction_review(["deterministic-table-parse"], how + " " + loc, BUNDLE_SHA, RURL)
def REVIEW_TEXT(loc):
    return extraction_review(["transcription"], "Sentence in Results 'PCR-cDNA libraries provide the most consistent recovery of validated fusion transcripts' asserted verbatim in the pinned XML by extract/extract_fusion_longread.py. " + loc, XML_SHA, XURL)

METHOD = {"CTAT-LR-Fusion": None, "FusionSeeker": "rna-fusion-20261009-method-fusionseeker", "GFSeeker": None, "Genion": None, "JAFFAL": "rna-fusion-20261009-method-jaffa", "LongGF": "rna-fusion-20261009-method-longgf"}
for c, desc in (("CTAT-LR-Fusion", "Long-read fusion transcript caller from the Trinity Cancer Transcriptome Analysis Toolkit."),
                ("GFSeeker", "Long-read gene fusion caller using a splicing-graph reference and re-alignment validation."),
                ("Genion", "Long-read gene fusion caller using chaining of alignments and segmental duplication filters.")):
    METHOD[c] = b.entity("method", b.rid("method", c), c, desc, [PRE],
        {"reported_name": c, "entity_level": "method", "source_locator": "Results; Methods 'Fusion caller configuration'",
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; versions are on configurations"}}}, method_types=["conventional_pipeline"])
_M = "Methods 'Reference genomes', 'Fusion caller configuration'; repository "
CFG_LOC = {"CTAT-LR-Fusion": _M + "Fusions/runtools/RunCTAT-LR-fusion.sh header", "GFSeeker": _M + "Fusions/runtools/RunGFSeeker.sh",
           "FusionSeeker": _M + "Fusions/runtools/Run_GFSLGF.sh header (caller versions, min_read_supp=2)", "Genion": _M + "Fusions/runtools/Run_GFSLGF.sh header (caller versions, min_read_supp=2)",
           "LongGF": _M + "Fusions/runtools/Run_GFSLGF.sh header (caller versions, min_read_supp=2)", "JAFFAL": _M + "Fusions/runtools/RunJAFFAL.sh"}
VER = {"FusionSeeker": "v1.0.1", "Genion": "v1.1.0", "LongGF": "v0.1.2", "JAFFAL": "JAFFA 2.3"}
CFG = {}
for c in CALLERS:
    attrs = {"reported_name": c, "foundation_model_eligible": False,
             "parameters": "minimap2 2.28 alignments to hg38 with GENCODE v44 (JAFFAL: UCSC GENCODE v43; Genion: Ensembl 110); calls with at least two supporting reads retained"
                           + ("; read-through retention enabled" if c == "JAFFAL" else ""),
             "access_reuse": "Public open-source software", "source_locator": CFG_LOC[c]}
    if c in VER:
        attrs["version"] = VER[c]
    else:
        attrs["missing_metadata"] = {"version": {"reason": "unreported", "note": "Not printed in the preprint or the pinned run scripts"}}
    CFG[c] = b.entity("configuration", b.rid("config", c), f"{c}{' ' + VER[c] if c in VER else ''} (Dorney et al. 2026)", f"{c} as run in the cited long-read fusion benchmark.", SIDS, attrs,
                      method_types=["conventional_pipeline"], links=[{"relation": "configuration_of", "target_id": METHOD[c]}])

LIM = ["Independent benchmark: the authors developed none of the six callers (Competing interests: none). Preprint, not peer reviewed.",
       "Caller versions for CTAT-LR-Fusion and GFSeeker are not stated."]
D_SIM = b.entity("dataset", b.rid("data", "badread-simulated-fusions"), "Badread simulated ONT transcriptomes with 400 Fusim fusion transcripts (Dorney et al. 2026)",
    "Simulated long-read RNA-seq: GENCODE transcriptome with HepG2-derived abundances plus Fusim fusions (100 each inter-chromosomal, intra-chromosomal, read-through and tri-gene; self-fusions excluded), Badread Nanopore2023 error model at 1, 10 and 100 Gb and mean identity 85%, 90% and 95%.", SIDS,
    {"population": "Nine simulated scenarios; 400 scored fusions (fewer present at low depth: Spiked_Number column)", "assay": "Badread v0.4.1 simulated ONT reads, 0.1% artificial chimeras, adapters removed with Porechop ABI",
     "split": "Simulation only", "source_locator": "Methods 'Simulation datasets'; repository stat_summary.tsv column 'Spiked_Number'",
     "missing_metadata": {"version": {"reason": "unreported"}}})
P_SIM = b.entity("protocol", b.rid("protocol", "simulated-fusions"), "Simulated long-read fusion detection, 400 fusions at three depths and three read identities (Dorney et al. 2026)",
    "Per-caller false and true calls, precision, recall and F1 against simulated fusions, calls with at least two supporting reads.", SIDS,
    {"protocol": "A call is a true positive only if both partner genes (Ensembl IDs, correct chromosome for paralogues) match a simulated fusion; partial recalls count as false positives. Recall = TP / simulated fusions present (Spiked_Number); precision = TP / (TP + FP); F1 their harmonic mean. Calls need at least two supporting reads.",
     "version": f"Repository commit {COMMIT[:12]}, Figures/Input_dataframes/stat_summary.tsv", "metric": "f1-score",
     "limitations": LIM + ["Simulated reads with synthetic fusions, not tumour RNA; most simulated fusions are not cancer drivers.",
                           "At 1 Gb the denominator (Spiked_Number) is 187 to 208 rather than 400, and at 10 Gb and 85% identity it is 397; the source does not explain why. Some callers have no row at 1 Gb (no calls).",
                           "Results prose gives false-call counts (GFSeeker 632, FusionSeeker 519, JAFFAL 106, CTAT-LR-Fusion 38) that do not match any row of the table; the scenario or filter they refer to is not stated.",
                           "Single simulation per scenario; no interval estimates. The FDR and Sensitivity columns repeat 1 minus precision and recall and are not recorded."],
     "source_locator": "Methods 'Benchmark evaluation criteria'; repository Precision_Recall_ReadSupp_stats.R lines 1-27; stat_summary.tsv"},
    links=[{"relation": "uses_data", "target_id": D_SIM}])
SIM_METRICS = [("False_Point", "false-positive-count", "lower", "count", "counted entity: calls not matching a simulated fusion, including partial recalls"),
               ("True_Point", "true-positive-count", "higher", "count", "counted entity: simulated fusions correctly called"),
               ("Precision", "precision", "higher", "fraction", None), ("Recall", "recall", "higher", "fraction", None), ("F1", "f1-score", "higher", "fraction", None)]
EV = {}
for c in CALLERS:
    EV[("sim", c)] = b.evaluation(b.rid("eval", c, "simulated-fusions"), f"{c} on simulated long-read fusions (Dorney et al. 2026)", SIDS, CFG[c], P_SIM, D_SIM, "independent_paper",
        {"protocol_id": P_SIM, "dataset_version": None, "split": "Simulation", "population": "400 simulated fusions per scenario", "inputs": "Simulated ONT reads aligned with minimap2",
         "adaptation": None, "metric_implementation": "Partner-gene match; partial recalls counted as false positives; at least two supporting reads", "aggregation": "One run per scenario", "budget": None},
        "stat_summary.tsv, rows Algorithm '" + c + "'", missing={"comparison.adaptation": {"reason": "inapplicable", "note": "No training"}})
for r in stat:
    c = r["Algorithm"]; scen = f"{r['depth']} {r['Sequence_Identity']}"
    for col, metric, d, unit, ud in SIM_METRICS:
        loc = f"stat_summary.tsv, row depth '{r['depth']}', Sequence_Identity '{r['Sequence_Identity']}', Algorithm '{c}', column '{col}'"
        extra = {"printed_value_basis": "Value as stored in the authors' repository table (full precision)"}
        miss = None
        if r[col] == "NA":
            miss = {"reason": "inapplicable", "note": "F1 undefined: no true positives, so precision and recall are both zero"}
            extra["undefined_reason"] = "F1 is undefined when precision and recall are both zero; printed 'NA'"
        b.result(b.rid("result", c, "sim", r["depth"], r["Sequence_Identity"], metric), f"{c} simulated {scen} {metric}", REPO, SIDS, EV[("sim", c)], r[col], metric, d, unit, loc,
                 REVIEW(loc, "Read the pinned repository file with extract/extract_fusion_longread.py; header, row count and caller labels asserted."),
                 qualifier=f"simulated fusions, {r['depth']} depth, {r['Sequence_Identity']} mean read identity, denominator {r['Spiked_Number']}",
                 unit_detail=ud, extra=extra, value_missing=miss)

D_SG = b.entity("dataset", b.rid("data", "sgnex-k562-mcf7"), "SG-NEx K562 and MCF7 ONT long-read RNA-seq (PCR-cDNA, direct cDNA, direct RNA), subsampled",
    "Public Singapore Nanopore Expression Project long-read RNA-seq of the K562 and MCF7 cancer cell lines, merged per library type and subsampled with rasusa to 1 to 10 Gb.", SIDS,
    {"population": "Two cancer cell lines; three ONT library types; full data and subsamples of 1, 2.5, 5, 7.5 and 10 Gb where available", "assay": "ONT PCR-cDNA, direct cDNA and direct RNA (SG-NEx)",
     "split": "Evaluation only", "source_locator": "Methods 'Public long-read datasets'; Results 'Known fusion recovery'",
     "missing_metadata": {"version": {"reason": "unreported", "note": "SG-NEx release not stated"}}})
P_SG = {}
for cell, n in (("K562", 6), ("MCF7", 53)):
    P_SG[cell] = b.entity("protocol", b.rid("protocol", "sgnex", cell), f"{cell} ONT long-read RNA-seq, recovery of {n} known fusions and count of other calls (Dorney et al. 2026)",
        f"Per-caller number of known {cell} fusions recovered and number of other (putative novel) calls, by library type and depth.", SIDS,
        {"protocol": f"Calls annotated against the authors' list of previously reported {cell} fusions ({n}); knownnumber counts distinct calls labelled known and novelnumber all other distinct calls (repository CellLineData/SGNex_DiscoveryNRecall.R).",
         "version": f"Repository commit {COMMIT[:12]}, Figures/Input_dataframes/counts_SGNex_summary.tsv.gz", "metric": "true-positive-count", "denominator": n,
         "limitations": LIM + [f"The known list ({n} fusions) comes from the literature; fusions missing from it count as other calls, so the other-call count mixes real unlisted fusions and false calls.",
                               "No read-support filter is applied in the counting script; the run-level two-read filter stated in Methods may or may not apply here.",
                               "Counts only; no precision or recall printed. Single run per library and depth.",
                               "knownnumber is the number of distinct call records the authors' script labels known (grouped by gene pair, chromosomes and fusion type); the script does not deduplicate them to listed fusions, so it is an upper bound on the number of listed fusions recovered."]
                        + (["Only six known K562 fusions, so recovery is coarse.",
                            "CTAT-LR-Fusion has no K562 PCR-cDNA rows at 7.5 or 10 Gb, and no caller has K562 direct-RNA rows above 2.5 Gb or direct-cDNA rows above 5 Gb; the source does not say why."] if cell == "K562" else []),
         "source_locator": "Results paragraph on SG-NEx K562 and MCF7; repository counts_SGNex_summary.tsv.gz and SGNex_DiscoveryNRecall.R"},
        links=[{"relation": "uses_data", "target_id": D_SG}])
for r in counts:
    c, cell = r["Algorithm"], r["Cell_Lines"]
    key = ("sg", cell, c)
    if key not in EV:
        EV[key] = b.evaluation(b.rid("eval", c, "sgnex", cell), f"{c} on SG-NEx {cell} ONT RNA-seq (Dorney et al. 2026)", SIDS, CFG[c], P_SG[cell], D_SG, "independent_paper",
            {"protocol_id": P_SG[cell], "dataset_version": None, "split": "Evaluation only", "population": f"{cell} cell line", "inputs": "ONT long reads aligned with minimap2",
             "adaptation": None, "metric_implementation": "Distinct calls matching the known list", "aggregation": "One run per library and depth", "budget": None},
            f"counts_SGNex_summary.tsv.gz, rows Cell_Lines '{cell}', Algorithm '{c}'", missing={"comparison.adaptation": {"reason": "inapplicable", "note": "No training"}})
    for col, metric, d, ud in (("knownnumber", "true-positive-count", "higher", f"counted entity: known {cell} fusions called"),
                               ("novelnumber", "count", "unknown", "counted entity: distinct calls not on the known list (putative novel or false)")):
        loc = f"counts_SGNex_summary.tsv.gz, row Source '{r['Source']}', Algorithm '{c}', column '{col}'"
        b.result(b.rid("result", c, cell, r["Library"], r["Sequencing_Depth"], col), f"{c} {cell} {r['Library']} {r['Sequencing_Depth']} {col}", REPO, SIDS, EV[key], r[col], metric, d, "count", loc,
                 REVIEW(loc, "Read the pinned repository file with extract/extract_fusion_longread.py; header, row count and caller labels asserted."),
                 qualifier=f"{r['Library']} library, {r['Sequencing_Depth']} depth" + (", known fusions" if col == "knownnumber" else ", calls not on the known list"), unit_detail=ud)

D_HUH = b.entity("dataset", b.rid("data", "huh7"), "Huh7 hepatocellular carcinoma cell line RNA-seq: ONT direct RNA, direct cDNA, PCR-cDNA, PacBio Kinnex and Illumina NovaSeq (Dorney et al. 2026)",
    "New sequencing of Huh7 with two biological replicates per ONT library type, plus PacBio Kinnex and matched Illumina 150-bp paired-end RNA-seq.", SIDS,
    {"population": "One cancer cell line; five library types; two replicates each", "assay": "ONT R10.4 cDNA and RNA004 direct RNA (MinION), PacBio Kinnex (IsoSeq3 cluster2), Illumina NovaSeq 150-bp paired-end",
     "split": "Evaluation only", "source_locator": "Methods 'Library preparation and RNA sequencing', 'Read processing'",
     "missing_metadata": {"accession": {"reason": "unavailable", "note": "Data availability statement gives the GEO/SRA accession as 'XXXXXXXXX'"}, "version": {"reason": "inapplicable"}}})
P_HUH = b.entity("protocol", b.rid("protocol", "huh7-known-fusions"), "Huh7 recovery of 34 previously reported fusions by library type, union of callers (Dorney et al. 2026)",
    "Number of the 34 previously reported Huh7 fusions recovered by any caller on each sequencing library type.", SIDS,
    {"protocol": "Known fusions recovered by the union of all six long-read callers (long-read libraries) or of JAFFA-direct, Arriba and STAR-Fusion (Illumina), calls with at least two spanning reads or pairs, both replicates.",
     "version": "Results 'PCR-cDNA libraries provide the most consistent recovery of validated fusion transcripts' paragraph 2", "metric": "true-positive-count", "denominator": 34,
     "limitations": LIM + ["Union of several callers per platform, so it compares sequencing platforms, not individual callers.",
                           "The Figure 4C legend refers to 25 curated known Huh7 or HCC fusions, while the text counts 34 previously reported Huh7 fusions, 21 of them recovered; the relation between the two lists is not explained.",
                           "None of the three RT-PCR or Sanger validated Huh7 fusions was detected by any library (Results).",
                           "ONT direct cDNA and direct RNA counts are shown only in Figure 4C and are not recorded.",
                           "Short-read callers' versions are not stated."],
     "source_locator": "Results paragraph quoted in the version field; Figure 4 legend (C, D)"},
    links=[{"relation": "uses_data", "target_id": D_HUH}])
UNION_METHOD = b.entity("method", b.rid("method", "union-of-fusion-callers"), "Union of fusion callers", "Fusion call set formed by the union of several callers' calls on the same library.", [PRE],
    {"reported_name": "Union of callers", "entity_level": "method", "source_locator": "Figure 4 legend (C-E)",
     "missing_metadata": {"version": {"reason": "inapplicable"}}}, method_types=["conventional_pipeline"])
for lib, label, callers, printed in (("pacbio-kinnex", "PacBio Kinnex", "six long-read callers", "20"), ("ont-pcr-cdna", "ONT PCR-cDNA", "six long-read callers", "17"),
                                     ("illumina", "Illumina", "JAFFA-direct, Arriba and STAR-Fusion", "15")):
    cfg = b.entity("configuration", b.rid("config", "union", lib), f"Union of {callers} on {label} (Dorney et al. 2026)", f"Union of {callers} applied to Huh7 {label} libraries.", SIDS,
        {"reported_name": label, "foundation_model_eligible": False, "parameters": f"Union of {callers}; calls with at least two spanning reads or pairs",
         "access_reuse": "Public open-source callers", "source_locator": "Figure 4 legend (C-E)",
         "missing_metadata": {"version": {"reason": "inapplicable", "note": "Combination of callers; individual versions partly unreported"}}},
        method_types=["conventional_pipeline"], links=[{"relation": "configuration_of", "target_id": UNION_METHOD}])
    ev = b.evaluation(b.rid("eval", "union", lib, "huh7"), f"Union of {callers} on Huh7 {label} (Dorney et al. 2026)", SIDS, cfg, P_HUH, D_HUH, "independent_paper",
        {"protocol_id": P_HUH, "dataset_version": None, "split": "Evaluation only", "population": "Huh7, two replicates", "inputs": f"{label} reads",
         "adaptation": None, "metric_implementation": "Partner-gene match to the known list", "aggregation": "Union over callers and replicates", "budget": None},
        "Results 'PCR-cDNA libraries provide the most consistent recovery of validated fusion transcripts' paragraph 2", missing={"comparison.adaptation": {"reason": "inapplicable"}})
    EV[("huh7", lib)] = ev
    loc = f"Results 'PCR-cDNA libraries provide the most consistent recovery of validated fusion transcripts' paragraph 2: '{label} ... ({printed})'" if lib != "illumina" else "Results 'PCR-cDNA libraries provide the most consistent recovery of validated fusion transcripts' paragraph 2: 'Illumina recovered 15'"
    b.result(b.rid("result", "union", lib, "huh7-known"), f"Union on Huh7 {label}, known fusions recovered", PRE, SIDS, ev, printed, "true-positive-count", "higher", "count", loc, REVIEW_TEXT(loc),
             qualifier="known Huh7 fusions recovered of 34, union of callers", unit_detail="counted entity: previously reported Huh7 fusions recovered")

UCN = "Select a tumour RNA fusion-detection workflow"
CIT = [{"source_id": PRE, "locator": "Results; Methods 'Simulation datasets', 'Public long-read datasets', 'Benchmark evaluation criteria'; Competing interests"},
       {"source_id": REPO, "locator": "Figures/Input_dataframes/stat_summary.tsv; counts_SGNex_summary.tsv.gz; SimulatedData/Data_Analysis_Scripts/Precision_Recall_ReadSupp_stats.R; CellLineData/SGNex_DiscoveryNRecall.R"}]
lims = lambda pid: next(x for x in b.records if x["id"] == pid)["attributes"]["limitations"]
GRP, TITLE = "dorney2026-longread", "Long-read fusion callers, independent benchmark (Dorney et al. 2026)"
JUDGE = {
    "sim": b.judgement(FUSION_UC, UCN, P_SIM, "Simulated long-read fusion detection (Dorney et al. 2026)", SIDS, "proxy",
        "Precision, recall, F1 and true and false call counts of six long-read fusion callers on 400 simulated fusions at nine depth and read-identity scenarios",
        "Proxy, not direct: an independent comparison of long-read callers with a complete truth set measures sensitivity and false calls, but the reads and fusions are simulated, not tumour RNA.",
        lims(P_SIM), CIT, GRP, TITLE, "Simulated reads, 400 fusions", 1, "f1-score"),
    "K562": b.judgement(FUSION_UC, UCN, P_SG["K562"], "K562 known-fusion recovery (Dorney et al. 2026)", SIDS, "direct",
        "Known K562 fusions recovered (of 6) and other calls per long-read caller, by ONT library type and depth",
        "Real cancer cell-line long-read RNA-seq scored against previously reported fusions measures sensitivity for known fusions and, through the other-call count, the review burden the use case asks about. The known list is small.",
        lims(P_SG["K562"]), CIT, GRP, TITLE, "K562, ONT libraries", 2, "true-positive-count"),
    "MCF7": b.judgement(FUSION_UC, UCN, P_SG["MCF7"], "MCF7 known-fusion recovery (Dorney et al. 2026)", SIDS, "direct",
        "Known MCF7 fusions recovered (of 53) and other calls per long-read caller, by ONT library type and depth",
        "Real cancer cell-line long-read RNA-seq scored against previously reported fusions measures sensitivity for known fusions and, through the other-call count, the review burden the use case asks about.",
        lims(P_SG["MCF7"]), CIT, GRP, TITLE, "MCF7, ONT libraries", 3, "true-positive-count"),
    "huh7": b.judgement(FUSION_UC, UCN, P_HUH, "Huh7 known-fusion recovery by platform (Dorney et al. 2026)", SIDS, "proxy",
        "Known Huh7 fusions recovered (of 34) by the union of callers on PacBio Kinnex, ONT PCR-cDNA and Illumina libraries of the same RNA",
        "Proxy, not direct: the same Huh7 RNA sequenced on PacBio Kinnex, ONT PCR-cDNA and Illumina gives the first linked short- versus long-read comparison on identical samples, but each value pools several callers (six long-read callers, three short-read callers for Illumina), so it compares platforms with unequal caller pools, not workflows a user would run.",
        lims(P_HUH), [CIT[0]], GRP, TITLE, "Huh7, platform comparison", 4, "true-positive-count"),
}
print(XML_SHA, BUNDLE_SHA, b.write())
if len(sys.argv) > 4:
    json.dump({"evaluations": {"|".join(k): v for k, v in EV.items()}, "judgements": JUDGE}, open(sys.argv[4], "w"), indent=1)
