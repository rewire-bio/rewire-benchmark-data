"""Build the gfm-guides-20261014-gpnmsa-gnomad batch: the gnomAD odds-ratio columns of GPN-MSA
Supplementary Table 4 (bioRxiv v2), which the first extraction (gfm-guides-20261014-gpnmsa) left out
for want of an odds-ratio metric concept.

Usage (python3 -I):
  build_gnomad.py <v2.pdf> <v2.txt from `pdftotext -layout v2.pdf v2.txt`> <repository-root> <batch-dir>

bioRxiv stamps every download (XMP dates, document IDs, trailer /ID), so a fresh copy does not
reproduce the pinned SHA-256 (see hash_scope on the source record). The script therefore accepts the
pinned bytes or a fresh copy of the same length, and ties the text layer to the reviewed version by
asserting that its ClinVar, COSMIC and OMIM cells equal all 102 values already in the store for this
table. It then asserts the caption, the column groups, the 'mean max' header, the 17 row labels and
the page, and transcribes the two gnomAD cells of each row.
"""
import csv, glob, hashlib, json, os, re, sys

PDF, TXT, REPO, OUT = sys.argv[1:5]
PDF_SHA = "10411077df1ae59614f9a9a9f85384103d54127ba67a9b3c469a4a2d6c33cee4"
PDF_SIZE = 2247726
PDF_URL = "https://www.biorxiv.org/content/10.1101/2023.10.10.561776v2.full.pdf"
DATE = "2026-10-14"
P = "gfm-guides-20261014-gpnmsa"
S_PDF = f"{P}-source-biorxiv-v2"
BENCH = f"{P}-benchmark-gpn-msa-vep"
AREAS = {"areas": ["dna-genomes"], "contexts": ["research"]}
NOTE = ("Extraction agent for rewire-benchmark-data issue #163 (metric concepts for the genomic foundation model guide "
        "evidence); extraction only, not a review. Pending an independent review-evidence pass.")

raw = open(PDF, "rb").read()
pdf_sha = hashlib.sha256(raw).hexdigest()
assert pdf_sha == PDF_SHA or len(raw) == PDF_SIZE, "PDF is neither the pinned bytes nor a same-length re-download"
text = open(TXT, encoding="utf-8").read()


def load(kind_dir):
    out = {}
    for path in glob.glob(os.path.join(REPO, kind_dir, "*.jsonl")):
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            out[r["id"]] = r
    return out


results = load("data/evidence/results")
evaluations = load("data/evidence/evaluations")
entities = {}
for path in glob.glob(os.path.join(REPO, "data/entities/*.jsonl")):
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        entities[r["id"]] = r

ROWS = [  # printed label, slug, system id
    ("Default", "default", f"{P}-config-ablation-default"),
    ("w/o MSA", "without-msa", f"{P}-config-ablation-without-msa"),
    ("MSA frequency (no neural net)", "msa-frequency", f"{P}-method-msa-frequency"),
    ("Combined phyloP and phastCons", "phylop-phastcons-combined", f"{P}-method-phylop-phastcons-combined"),
    ("Train on 50% most conserved", "train-50pct-conserved", f"{P}-config-ablation-train-50pct-conserved"),
    ("Train on 100% of genome", "train-100pct-genome", f"{P}-config-ablation-train-100pct-genome"),
    ("Include closest primates", "include-closest-primates", f"{P}-config-ablation-include-closest-primates"),
    ("51 mammals", "51-mammals", f"{P}-config-ablation-51-mammals"),
    ("51 vertebrates", "51-vertebrates", f"{P}-config-ablation-51-vertebrates"),
    ("Don’t upweight conserved", "no-upweight-conserved", f"{P}-config-ablation-no-upweight-conserved"),
    ("Don’t replace non-conserved", "no-replace-nonconserved", f"{P}-config-ablation-no-replace-nonconserved"),
    ("Window size = 256", "window-256", f"{P}-config-ablation-window-256"),
    ("Window size = 64", "window-64", f"{P}-config-ablation-window-64"),
    ("Window size = 32", "window-32", f"{P}-config-ablation-window-32"),
    ("Window size = 16", "window-16", f"{P}-config-ablation-window-16"),
    ("Window size = 8", "window-8", f"{P}-config-ablation-window-8"),
    ("Window size = 4", "window-4", f"{P}-config-ablation-window-4"),
]

start = text.index("Supplementary Table 4: Ablation study.")
end = text.index("Supplementary Table 5: Training hyperparameters")
block = text[start:end]
flat_caption = re.sub(r"\s+", " ", block)
CAPTION = ("gnomAD (odds ratio): same approach as Figure 2d, including all variant types, but subsetting the rare variants "
           "to match the number of common variants.")
assert CAPTION in flat_caption, "caption gnomAD sentence"
assert re.search(r"ClinVar\s+COSMIC\s+OMIM\s+gnomAD", block), "column groups"
assert re.search(r"mean\s+max\s+mean\s+max\s+mean\s+max\s+mean\s+max", block), "mean/max header"
assert text[:start].count("\f") + 1 == 23, "Supplementary Table 4 page"
FIG2F = ("Enrichment of rare (singletons) vs. common (MAF > 5%) gnomAD variants (subset) in the tail of deleterious scores "
         "(the threshold was chosen such that each score makes 30 false discoveries). Odds ratios and p-values were computed "
         "using one-sided Fisher’s exact test.")
flat = re.sub(r"\s+", " ", text).replace("(f ) ", "(f) ")
assert FIG2F in flat, "Figure 2f caption"
ABL = ("gnomAD (ablation set): enrichment of rare vs. common gnomAD variants in the tail of deleterious scores. "
       "Because of the large size of the full data, we subset the rare variants to match the number of common variants per consequence.")
assert ABL in flat, "Methods 'Additional VEP metrics' gnomAD (ablation set)"

NUM = r"(\d+\.\d+)"
data_lines = [l for l in block.splitlines() if re.search(r"\d+\.\d+\s*$", l)]
assert len(data_lines) == len(ROWS) == 17, len(data_lines)
parsed = {}
for label, slug, system in ROWS:
    m = re.search(r"^\s*" + re.escape(label) + r"\s+" + r"\s+".join([NUM] * 8) + r"\s*$", block, re.M)
    assert m, f"row not found: {label}"
    parsed[label] = m.groups()
    assert system in entities, system
    # tie the text layer to the reviewed version: the six ClinVar, COSMIC and OMIM cells must equal the store
    for key, idx in [("clinvar", 0), ("cosmic", 2), ("omim", 4)]:
        for agg, off in [("mean", 0), ("max", 1)]:
            stored = results[f"{P}-result-ablation-{slug}-{key}-{agg}"]["attributes"]["printed_value"]
            assert stored == m.group(idx + off + 1), (label, key, agg, stored, m.group(idx + off + 1))
    # reuse the origin the reviewed evaluations of the same row carry
    parsed[label] = (m.groups(), evaluations[f"{P}-eval-ablation-{slug}-clinvar"]["attributes"]["origin"])

records, claims_rows = [], []


def add(rec):
    assert rec["id"] not in entities and rec["id"] not in evaluations and rec["id"] not in results, rec["id"]
    records.append(rec)
    return rec["id"]


D_GNOMAD = add({"id": f"{P}-data-gnomad-rare-vs-common-ablation-set", "kind": "dataset",
                "name": "gnomAD rare (singletons) vs common variants, ablation set (GPN-MSA paper)",
                "description": "gnomAD v3.1.2 singletons as the rare class and variants with minor allele frequency above 5% as the common class, all variant types, with rare variants subsampled to match the number of common variants per consequence.",
                "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF], "links": [],
                "attributes": {
                    "version": "gnomAD v3.1.2 (allele number at least 25,000 and official quality-control flags)",
                    "split": "Whole labelled set; no training on labels (zero-shot scores)",
                    "population": "gnomAD singletons versus gnomAD variants with MAF > 5%, all variant types; rare variants subsampled to the number of common variants per consequence",
                    "source_locator": "Methods 'VEP data sources' (gnomAD) and 'Additional VEP metrics' ('gnomAD (ablation set)'); Supplementary Table 4 caption",
                    "missing_metadata": {"denominator": {"reason": "unreported", "note": "Variant counts of the ablation set are not printed"}},
                }})
PROTO = add({"id": f"{P}-protocol-ablation-gnomad-odds-ratio", "kind": "protocol",
             "name": "gnomAD rare vs common enrichment in the deleterious tail, odds ratio (GPN-MSA Supplementary Table 4)",
             "description": "Odds ratio of rare versus common gnomAD variants among the variants a score places in its deleterious tail, the tail threshold set so that each score makes 30 false discoveries.",
             "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF],
             "links": [{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": D_GNOMAD}],
             "attributes": {
                 "protocol": "Each model or score is applied zero-shot (no training on these labels). Variants are ranked by score; the deleterious tail is cut where the score makes 30 false discoveries (common variants), and the odds ratio of rare versus common variants in the tail is computed with a one-sided Fisher's exact test. All variant types, with rare variants subsampled to match the number of common variants. For each ablation setting three replicate models with different seeds were trained where applicable; the table prints the mean and the maximum over seeds.",
                 "version": "bioRxiv v2 Supplementary Table 4",
                 "metric": "odds-ratio", "metric_direction": "higher", "unit": "unitless",
                 "limitations": [
                     "Benchmark built and run by the GPN-MSA authors (author-reported).",
                     "The caption says 'same approach as Figure 2d'; in v2 the gnomAD enrichment panel is Figure 2f (the caption's figure letters are off by two, as for the other columns).",
                     "The false-discovery count for the ablation table is not restated; Figure 2f and Methods 'Main VEP metrics' give 30 as the example threshold.",
                     "Variant counts and p-values are not printed in Supplementary Table 4.",
                 ],
                 "source_locator": "Supplementary Table 4 caption and column group 'gnomAD'; Figure 2 caption panel (f); Methods 'Main VEP metrics' (gnomAD) and 'Additional VEP metrics' ('gnomAD (ablation set)')",
             }})

QUAL = ("rare (singletons) versus common (MAF > 5%) gnomAD variants in the tail of deleterious scores, threshold at 30 false "
        "discoveries, one-sided Fisher's exact test; all variant types, rare subsampled to the common count; ")
for label, slug, system in ROWS:
    vals, origin = parsed[label]
    ev = add({"id": f"{P}-eval-ablation-{slug}-gnomad", "kind": "evaluation",
              "name": f"{label} on gnomAD (GPN-MSA Supplementary Table 4)",
              "description": "Published comparison transcribed from the pinned source; not reproduced.",
              "status": "needs_review", "facets": dict(AREAS), "source_ids": [S_PDF],
              "links": [{"relation": "system", "target_id": system},
                        {"relation": "assessment", "target_id": PROTO},
                        {"relation": "data", "target_id": D_GNOMAD}],
              "attributes": {
                  "origin": origin, "protocol": PROTO, "version": "bioRxiv v2 as retrieved 2026-10-14",
                  "comparison": {"protocol_id": PROTO, "dataset_version": None, "split": "Whole labelled set",
                                 "population": None,
                                 "inputs": "Reference genome and multispecies alignment around each variant (GPN-MSA rows); alignment column or conservation scores (method rows)",
                                 "adaptation": "zero-shot",
                                 "metric_implementation": "Odds ratio from a one-sided Fisher's exact test on rare versus common variants above the 30-false-discovery threshold",
                                 "aggregation": "Mean and maximum over three random seeds where applicable (printed as separate columns)",
                                 "budget": None},
                  "source_locator": f"Supplementary Table 4 row '{label}', column group 'gnomAD'",
                  "missing_metadata": {"comparison.dataset_version": {"reason": "unreported", "note": "gnomAD release printed in Methods; the subsampled variant set and its size are not"},
                                       "comparison.population": {"reason": "unreported"},
                                       "comparison.budget": {"reason": "unreported"}},
              }})
    for agg, off in [("mean", 0), ("max", 1)]:
        pv = vals[6 + off]
        rid = f"{P}-result-ablation-{slug}-gnomad-{agg}"
        loc = f"Supplementary Table 4 (PDF page 23), row '{label}', column 'gnomAD' / '{agg}'"
        add({"id": rid, "kind": "result",
             "name": f"{label} gnomAD odds ratio ({agg} over seeds)",
             "description": "Reported measurement transcribed from the pinned source. Not independently reproduced.",
             "status": "needs_review", "facets": {}, "source_ids": [S_PDF],
             "links": [{"relation": "evaluation", "target_id": ev}],
             "attributes": {
                 "printed_value": pv, "numeric_value": pv,
                 "metric": "odds-ratio", "metric_direction": "higher", "unit": "unitless",
                 "metric_qualifier": QUAL + ("mean over three random seeds" if agg == "mean" else "maximum over three random seeds") + "; zero-shot",
                 "source_locator": loc,
                 "missing_metadata": {"uncertainty": {"reason": "unreported", "note": "Only mean and max over seeds are printed"}},
                 "review": {"method": ["pdf-text-parse"], "reviewer": ["claude"], "reviewer_note": NOTE, "date": DATE,
                            "artifact_sha256": PDF_SHA, "retrieval_url": PDF_URL,
                            "method_note": ("Parsed the pdftotext 26.08.0 -layout text of a 2026-10-14 re-download of the v2 PDF "
                                            f"(same length as the pinned file; SHA-256 {pdf_sha}) with extract/build_gnomad.py; caption, column "
                                            "groups, 'mean max' header, the 17 row labels and the page asserted, and the row's ClinVar, COSMIC "
                                            "and OMIM cells asserted equal to the reviewed store values."),
                            "note": ("Extracted, not reviewed. For rows without a neural network (MSA frequency, combined phyloP and "
                                     "phastCons) three seeds do not apply and mean equals max. The review-evidence pass must re-check "
                                     "this cell against the pinned PDF.")},
             }})
        claims_rows.append([rid, S_PDF, loc, pv, "result"])

for r in records:  # the store keeps missing_metadata keys sorted (normalizeAttributes)
    if "missing_metadata" in r["attributes"]:
        r["attributes"]["missing_metadata"] = dict(sorted(r["attributes"]["missing_metadata"].items()))
records.sort(key=lambda r: r["id"])
assert len({r["id"] for r in records}) == len(records)
with open(os.path.join(OUT, "batch.jsonl"), "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
with open(os.path.join(OUT, "claims.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["record_id", "source_id", "locator", "printed_value", "review_scope"])
    w.writerows(sorted(claims_rows))
from collections import Counter
counts = Counter(r["kind"] for r in records)
assert counts["result"] == 34, counts
print(dict(sorted(counts.items())), "PDF sha256", pdf_sha)
