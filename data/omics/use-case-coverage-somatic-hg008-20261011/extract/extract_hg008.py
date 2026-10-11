"""Hasan 2026 (Research Square rs-11210923 v1): HG008 external evaluation of Mutect2, Strelka2, DeepSomatic
and three deterministic ensembles. Every cell of Zenodo Tables 1, 2 and 4.

Usage: python3 -I extract_hg008.py <paper.pdf> <zenodo.zip> <batch-folder>
Reads the three TSVs from the pinned Zenodo zip, checks each member against the archive's SHA256SUMS,
and asserts the row labels.
"""
import sys, os, io, csv, gzip, hashlib, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256, SOMATIC_UC

pdf, zpath, folder = sys.argv[1:4]
PDF_SHA, ZIP_SHA = sha256(pdf), sha256(zpath)
assert PDF_SHA == "358502e2394c1f90214889c40aae8b29d2836cddbcf55460688d7fda051dc1c3", PDF_SHA
assert ZIP_SHA == "629921b1198f4a5290d191857d13f98e54a1d132d722caf0ac83805f7e24a40d", ZIP_SHA
ROOT = "P003-T001-publication-data-v1.0.0-DOI-bound/"
z = zipfile.ZipFile(zpath)
sums = dict(reversed(l.split("  ", 1)) for l in z.read(ROOT + "SHA256SUMS").decode().splitlines() if l.strip())
TABLES = {"t1": "tables/Table1_HG008_primary_metrics.tsv", "t2": "tables/Table2_HG008_variant_class_metrics.tsv",
          "t4": "tables/Table4_HG008_sensitivity_all_region.tsv"}
raw, rows = {}, {}
for k, p in TABLES.items():
    raw[k] = z.read(ROOT + p)
    assert hashlib.sha256(raw[k]).hexdigest() == sums[p], p
    rows[k] = list(csv.DictReader(io.StringIO(raw[k].decode()), delimiter="\t"))
METHODS = ["Mutect2", "Strelka2", "DeepSomatic", "Union", "Majority", "StrictIntersection"]
assert [r["Method"] for r in rows["t1"]] == METHODS
assert [r["Method"] for r in rows["t4"]] == METHODS
assert [(r["Method"], r["Class"]) for r in rows["t2"]] == [(m, c) for m in METHODS for c in ("SNV", "INDEL")]

os.makedirs(os.path.join(folder, "artifacts"), exist_ok=True)
arch = {}
for k, p in TABLES.items():
    out = os.path.join(folder, "artifacts", os.path.basename(p) + ".gz")
    with open(out, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as g:
            g.write(raw[k])
    arch[p] = (hashlib.sha256(raw[k]).hexdigest(), sha256(out))

ZURL = "https://zenodo.org/api/records/22998005/files/P003-T001-publication-data-v1.0.0-zenodo-final.zip/content"
PURL = "https://assets-eu.researchsquare.com/files/rs-11210923/v1/64524534-bebe-4227-867b-bdb799621e9b.pdf"
b = Batch(folder, "somatic-hg008-20261011", ["dna-genomes"])
LIM_SRC = ["Single-author preprint, not peer reviewed. The author founded AmbioSpire LLC, under which the study was run (Competing Interests).",
           "The author reports that the exact historical scoring and bootstrap source code was not retained; an internal reimplementation reproduced the numbers (Results; Online Methods 'Executable-source custody limitation'). No external replication."]
SRC = b.source("somatic-hg008-20261011-source-hasan2026", "Prospectively frozen external benchmarking reveals benchmark-context dependence in somatic variant calling", {
    "url": "https://doi.org/10.21203/rs.3.rs-11210923/v1", "artifact_url": PURL,
    "version": "Research Square preprint rs-11210923 version 1, posted 2026-10-05; manuscript PDF (16 pages)",
    "retrieved_at": "2026-10-11T21:39:12Z", "artifact_sha256": PDF_SHA, "doi": "10.21203/rs.3.rs-11210923/v1",
    "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "application/pdf", "limitations": LIM_SRC},
    "Primary source (preprint) retrieved and hashed for the 2026-10-11 oncology use-case literature pass.")
ZSRC = b.source("somatic-hg008-20261011-source-hasan2026-zenodo", "AmbioSpire P003/T001 publication source data and reproducibility package v1.0.0 (Zenodo)", {
    "url": "https://doi.org/10.5281/zenodo.22998005", "artifact_url": ZURL,
    "version": "Zenodo record 22998005, version 1.0.0, published 2026-09-27; file P003-T001-publication-data-v1.0.0-zenodo-final.zip (1,934,562 bytes, md5 a1fdab6108197602f07f72db77d9f996)",
    "retrieved_at": "2026-10-11T21:39:34Z", "artifact_sha256": ZIP_SHA, "doi": "10.5281/zenodo.22998005",
    "publication_status": "official_project_source", "licence": "CC-BY-4.0", "media_type": "application/zip",
    "hash_scope": "SHA-256 of the downloaded zip. Member SHA-256 values for the extracted tables: " + "; ".join(f"{p} {h}" for p, (h, _) in arch.items()) + " (each equals the archive's own SHA256SUMS entry).",
    "limitations": LIM_SRC}, "Author-deposited result tables for the HG008 evaluation, retrieved and hashed for the 2026-10-11 oncology use-case literature pass.")
SIDS = [SRC, ZSRC]

def REVIEW(loc, member):
    return extraction_review(["deterministic-table-parse"],
        f"Read {member} from the pinned Zenodo zip with extract/extract_hg008.py; member SHA-256 checked against the archive's SHA256SUMS; method and class row labels asserted. {loc}",
        ZIP_SHA, ZURL)

DATA = b.entity("dataset", b.rid("data", "hg008-wgs"), "NIST/GIAB HG008 tumour-normal WGS (HG008-T pancreatic cancer cell line, matched normal), HG008-T draft somatic small-variant benchmark v0.3",
    "Matched tumour-normal whole-genome data for the GIAB HG008 cancer cell line and its draft clonal/truncal somatic small-variant truth set, as used by Hasan 2026.", SIDS,
    {"version": "NIST_HG008-T_somatic-smvar_DraftBenchmark_V0.3-20260425 (truth VCF SHA-256 6ff5b215e0dc634c85da6164cffbd5790233258fcc48c88a598331430b061cad)",
     "population": "One tumour-normal pair (HG008-T and matched normal). Primary region 'nogermlineinterference': 14,014 truth variants (9,078 SNVs, 4,936 indels). Region 'all': 18,207 truth variants (TP + FN in Table 4).",
     "split": "External test only: the procedure was developed on SEQC2 HCC1395/HCC1395BL (v1.2.1) and frozen before HG008 truth access.",
     "assay": "Tumour-normal WGS (platform, read length and coverage not stated) aligned with BWA-MEM2 v2.3 to GRCh38_GIABv3_no_alt_analysis_set_maskedGRC_decoys_MAP2K3_KMT2C_KCNJ18",
     "source_locator": "Online Methods 'Development and external resources', 'Reference and alignment', 'Benchmark regions'; Results 'Caller and deterministic-consensus performance'; Zenodo metadata/benchmark_resource_identities.tsv",
     "missing_metadata": {"accession": {"reason": "unreported", "note": "Read accessions for HG008 are not given; truth and BED bytes are protected and not redistributed"}}})

LIMS = ["Single-author preprint, not peer reviewed; the author founded AmbioSpire LLC, under which the study was run.",
        "One cell-line tumour-normal pair (HG008) and a draft truth set (HG008-T v0.3, clonal/truncal variants only).",
        "Matching is exact CHROM/POS/REF/ALT after normalisation; no representation-aware comparison, so complex indels may count as errors.",
        "The author does not establish that DeepSomatic's bundled WGS model was trained independently of HCC1395/SEQC2; HG008 itself is described as external to the study's development.",
        "Exact caller command lines and runtime flags were not retained; versions and container digests are.",
        "Union, majority and strict intersection are the author's ensembles (author_reported); the individual callers were run, not developed, by the author.",
        "The original scoring and bootstrap code was not retained; the author reports that a later internal reimplementation reproduced the numbers. No external replication.",
        "Whether DeepSomatic 1.10.0's bundled WGS model was trained with HG008 data is stated neither in the source nor in the DeepSomatic README, metrics page and WGS case study (github.com/google/deepsomatic, commit 09d605a966e5dcb10361cd036e05cb79d21b0062, checked 2026-10-11); the DeepSomatic paper was not checked."]
H3 = "The primary region (nogermlineinterference) holds 14,014 of the 18,207 truth variants in the full benchmark; the rest are sites with germline interference. Over the full benchmark (Table 4) overall F1 is 0.70 to 0.79 rather than 0.78 to 0.91, and in the germline-interference stratum DeepSomatic F1 is 0.0528 (Results)."
ALL_CI = {"Mutect2": ("0.7854", "0.7980"), "Strelka2": ("0.6691", "0.7205"), "DeepSomatic": ("0.7689", "0.7822"),
          "Union": ("0.7018", "0.7521"), "Majority": ("0.7875", "0.8003"), "StrictIntersection": ("0.7316", "0.7456")}
PROTOS = {
    "primary-overall": ("t1", None, "HG008 primary region (nogermlineinterference), SNVs and indels combined", 14014, "Table 1", "All small variants, primary region", 3),
    "primary-snv": ("t2", "SNV", "HG008 primary region (nogermlineinterference), SNVs", 9078, "Table 2, Class 'SNV'", "SNVs, primary region", 1),
    "primary-indel": ("t2", "INDEL", "HG008 primary region (nogermlineinterference), indels", 4936, "Table 2, Class 'INDEL'", "Indels, primary region", 2),
    "all-region-overall": ("t4", None, "HG008 all-benchmark region (sensitivity analysis), SNVs and indels combined", 18207, "Table 4", "All small variants, all-benchmark region", 4),
}
P, PL = {}, {}
for key, (t, cls, label, denom, loc, stratum, order) in PROTOS.items():
    lims = LIMS + (["Prespecified sensitivity region that includes variants near germline variants. Its 95% block-bootstrap F1 intervals are printed in the manuscript Results (Supplementary Table 2); that analysis was prespecified but executed after the primary external evaluation."] if key.startswith("all") else
                   ["Intervals are 95% block-bootstrap percentile intervals over 5-Mb genomic blocks (10,000 replicates); they describe spatial variation within this benchmark, not between tumours.", H3])
    PL[key] = lims
    P[key] = b.entity("protocol", b.rid("protocol", key), f"{label}, Mutect2, Strelka2, DeepSomatic and ensembles (Hasan 2026 {loc})",
        f"TP, FP, FN, precision, recall and F1 of PASS calls from three callers and three deterministic ensembles: {label}.", SIDS,
        {"protocol": "Tumour-normal calling with each caller; PASS calls restricted, split, left-normalised and deduplicated (bcftools 1.20); exact CHROM/POS/REF/ALT match to the truth VCF within the benchmark region. Precision TP/(TP+FP), recall TP/(TP+FN), F1 their harmonic mean. Ensembles: union (at least one caller), majority (at least two), strict intersection (all three).",
         "version": f"Zenodo v1.0.0 {TABLES[t]}" + (f", Class '{cls}'" if cls else ""), "metric": "f1-score", "denominator": denom,
         "limitations": lims, "source_locator": f"Online Methods 'PASS filtering, normalization and exact comparison', 'Consensus definitions and metrics', 'Benchmark regions'; Zenodo {TABLES[t]}"},
        links=[{"relation": "uses_data", "target_id": DATA}])

CFG = {}
CFG_SPEC = {
    "Mutect2": ("somatic-20261009-method-mutect2", "Mutect2 (GATK 4.6.2.0)", "GATK 4.6.2.0", "broadinstitute/gatk:4.6.2.0, digest sha256:71b17ee42d149e8ec112603f5305c873ab60d93949ef8bb62a4fff85427f56fb4; tumour-normal mode; PASS calls", ["conventional_pipeline"]),
    "Strelka2": ("somatic-20261009-method-strelka", "Strelka2 2.9.10", "2.9.10", "quay.io/biocontainers/strelka:2.9.10--h9ee0642_1, digest sha256:e6133fa935d444aaf3aa04b57256a580d9b3498298fc17cb5f4a9818116105ec5; PASS calls", ["conventional_pipeline"]),
    "DeepSomatic": ("somatic-20261009-method-deepsomatic", "DeepSomatic 1.10.0, bundled WGS model", "1.10.0", "google/deepsomatic:1.10.0, digest sha256:6cd98c41781cdc1a2916d8029bedef70a57b87d41f933bd4cf259c80f291e27b6; bundled whole-genome model (manifest SHA-256 3d909228d0224370959222cfc7f67d92ab76436d4455be92b9fb90cdb9ff7a66); no retraining or tuning; PASS calls", ["supervised_machine_learning"]),
    "Union": ("somatic-20261009-method-majority-vote", "Union of Mutect2, Strelka2 and DeepSomatic (at least one caller)", None, "Variant kept when at least one of Mutect2, Strelka2 and DeepSomatic reports it", ["conventional_pipeline"]),
    "Majority": ("somatic-20261009-method-majority-vote", "Majority of Mutect2, Strelka2 and DeepSomatic (at least two callers)", None, "Variant kept when at least two of Mutect2, Strelka2 and DeepSomatic report it", ["conventional_pipeline"]),
    "StrictIntersection": ("somatic-20261009-method-majority-vote", "Strict intersection of Mutect2, Strelka2 and DeepSomatic (all three callers)", None, "Variant kept only when all three of Mutect2, Strelka2 and DeepSomatic report it", ["conventional_pipeline"]),
}
for m, (fam, name, ver, params, mt) in CFG_SPEC.items():
    attrs = {"reported_name": m, "foundation_model_eligible": False, "parameters": params,
             "access_reuse": "Public open-source software" if m in ("Mutect2", "Strelka2", "DeepSomatic") else "Ensemble rule defined in the source; no released implementation (Zenodo archive holds no executable code)",
             "source_locator": "Online Methods 'Variant callers and retained software identities' and 'Consensus definitions and metrics'; Zenodo metadata/software_versions.tsv"}
    if ver:
        attrs["version"] = ver
    else:
        attrs["missing_metadata"] = {"version": {"reason": "inapplicable", "note": "Deterministic ensemble rule over the three versioned callers"}}
    CFG[m] = b.entity("configuration", b.rid("config", m), f"{name} (Hasan 2026)", f"{m} as run in the cited HG008 evaluation.", SIDS, attrs, method_types=mt,
                      links=[{"relation": "configuration_of", "target_id": fam}])

METRICS = [("TP", "true-positive-count", "higher", "count", "counted entity: truth variants matched by a PASS call"),
           ("FP", "false-positive-count", "lower", "count", "counted entity: PASS calls absent from the truth set"),
           ("FN", "false-negative-count", "lower", "count", "counted entity: truth variants with no matching PASS call"),
           ("Precision", "precision", "higher", "fraction", None), ("Recall", "recall", "higher", "fraction", None), ("F1", "f1-score", "higher", "fraction", None)]
EVALS = {}
for key, (t, cls, label, denom, loc, stratum, order) in PROTOS.items():
    p = P[key]
    sel = [r for r in rows[t] if cls is None or r["Class"] == cls]
    assert len(sel) == 6
    for r in sel:
        m = r["Method"]
        assert int(r["TP"]) + int(r["FN"]) == denom, (key, m)
        origin = "author_reported" if m in ("Union", "Majority", "StrictIntersection") else "independent_paper"
        ev = b.evaluation(b.rid("eval", m, key), f"{m} on {label} (Hasan 2026)", SIDS, CFG[m], p, DATA, origin,
            {"protocol_id": p, "dataset_version": "HG008-T draft somatic small-variant benchmark v0.3",
             "split": "External test; procedure frozen on HCC1395 before HG008 truth access", "population": "One HG008 tumour-normal pair",
             "inputs": "Tumour and matched-normal WGS alignments", "adaptation": None,
             "metric_implementation": "Exact normalised CHROM/POS/REF/ALT match of PASS calls within the region",
             "aggregation": "Single pair; 95% block-bootstrap interval on F1" if t != "t4" else "Single pair", "budget": None},
            f"Zenodo {TABLES[t]}, row '{m}'" + (f", Class '{cls}'" if cls else ""), missing={"comparison.adaptation": {"reason": "inapplicable", "note": "No training or tuning on HG008"}})
        EVALS.setdefault(key, []).append(ev)
        qual = {"t1": "SNVs and indels, HG008 primary region", "t4": "SNVs and indels, HG008 all-benchmark region"}.get(t) or f"{'SNV' if cls == 'SNV' else 'indel'} only, HG008 primary region"
        for col, metric, d, unit, ud in METRICS:
            locator = f"Zenodo {TABLES[t]}, row '{m}'" + (f", Class '{cls}'" if cls else "") + f", column '{col}'"
            unc = None
            if col == "F1" and "F1_CI_low" in r:
                unc = {"type": "confidence_interval", "lower": r["F1_CI_low"], "upper": r["F1_CI_high"], "level": 0.95, "method": "bootstrap_percentile",
                       "resamples": 10000, "printed": f"{r['F1_CI_low']} to {r['F1_CI_high']}", "source_column": "F1_CI_low, F1_CI_high",
                       "note": "Genomic block bootstrap over 5-Mb blocks, linear percentile interval; spatial variation within the benchmark region, not between tumours"}
            elif col == "F1" and t == "t4":
                lo, hi = ALL_CI[m]
                unc = {"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "method": "bootstrap_percentile", "resamples": 10000, "printed": f"{lo}\u2013{hi}",
                       "source_column": "Manuscript Results, 'Sensitivity analyses show benchmark-context dependence without establishing population generalization', paragraph 2 (Supplementary Table 2)",
                       "note": "Genomic block bootstrap over 5-Mb blocks, linear percentile interval; prespecified, but executed after the primary external evaluation; spatial variation within the benchmark region, not between tumours"}
            b.result(b.rid("result", m, key, metric), f"{m} {label} {metric}", ZSRC, SIDS, ev, r[col], metric, d, unit, locator,
                     REVIEW(locator, TABLES[t]), qualifier=qual, unit_detail=ud, uncertainty=unc,
                     extra={"printed_value_basis": "Value as stored in the author's Zenodo table (six decimals); the manuscript prints some of these rounded to four decimals"})

UCN = "Select a tumour DNA somatic variant-calling workflow"
CIT = [{"source_id": SRC, "locator": "Results 'Caller and deterministic-consensus performance differ in the HG008 external benchmark'; Online Methods; Declarations"},
       {"source_id": ZSRC, "locator": "tables/Table1_HG008_primary_metrics.tsv, Table2_HG008_variant_class_metrics.tsv, Table4_HG008_sensitivity_all_region.tsv"}]
JUDGE = {}
for key, (t, cls, label, denom, loc, stratum, order) in PROTOS.items():
    JUDGE[key] = b.judgement(SOMATIC_UC, UCN, P[key], f"{label} (Hasan 2026)", SIDS, "direct",
        f"TP, FP, FN, precision, recall and F1 (with block-bootstrap interval where printed) of Mutect2, Strelka2, DeepSomatic and three ensembles on {label}",
        "A real tumour-normal cell-line pair with a NIST draft truth set, scored by someone who developed none of the callers, measures exactly the per-caller precision, recall and F1 the use case asks for, and adds the HG008 benchmark that the use case lists as a gap.",
        PL[key], CIT,
        "hasan2026-hg008", "Mutect2, Strelka2, DeepSomatic and ensembles on HG008 (Hasan 2026)", stratum, order, "f1-score")
counts = b.write()
print(PDF_SHA, ZIP_SHA, counts)
import json
if len(sys.argv) > 4:
    json.dump({"evaluations": EVALS, "judgements": JUDGE, "archives": arch}, open(sys.argv[4], "w"), indent=1)
