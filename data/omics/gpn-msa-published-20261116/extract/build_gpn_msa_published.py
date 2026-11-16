"""Build the gpn-msa-published-20261116 batch and compare the published values with the stored ones.

Usage (python3 -I):
  build_gpn_msa_published.py <artifact-dir> <store-root> <out-dir>

<artifact-dir> holds the retrieved published-version artifacts, named exactly:

  nature_article.html            https://www.nature.com/articles/s41587-024-02511-w
  fig2.html                      https://www.nature.com/articles/s41587-024-02511-w/figures/2
  tab1.html                      https://www.nature.com/articles/s41587-024-02511-w/tables/1
  41587_2024_2511_Tab1_ESM.jpg   https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-024-02511-w/MediaObjects/41587_2024_2511_Tab1_ESM.jpg
  out_MOESM1_ESM.pdf             https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-024-02511-w/MediaObjects/41587_2024_2511_MOESM1_ESM.pdf
  moesm1.txt                     pdftotext -layout out_MOESM1_ESM.pdf moesm1.txt

None of these may be redistributed, so the batch folder keeps no copy. Re-download them to rerun.

What the script checks:

  1. The SHA-256 of every artifact except nature_article.html, whose bytes nature.com varies
     between retrievals (advertising and session markup). For that page the script asserts the
     passages used instead, and prints the hash of the copy it was given.
  2. The Extended Data Table 1 caption, the Figure 2 panel captions with their sample sizes, and
     the Supplementary Information listing, verbatim.
  3. The published Supplementary Tables 1 and 2 parsed from the Supplementary Information text
     layer with their row labels asserted.
  4. TAB1, the transcription of Extended Data Table 1. That table is published only as a raster
     image, so its 136 values were read by eye from the pinned JPEG. The script cannot verify
     them against a text layer; it compares them with the stored bioRxiv v2 values and writes
     comparison.tsv, which is the evidence a reviewer re-reads the image against.
  5. The stored results: 138 from the preprint source, 136 of them Supplementary Table 4 cells.

It writes batch.jsonl to <out-dir> and extract/comparison.tsv under it.
"""
import hashlib
import json
import os
import re
import sys

ART, STORE, OUT = sys.argv[1:4]

SHA = {
    "fig2.html": "d031178b99df61866b0a302fdfe35f37a18c4f3c3bdb31c5b232514dd7cbd5d6",
    "tab1.html": "abe7bcaf55b0354a7f50f8d2cd91b47c16bc189cfa45b8f2ac0c1fb99dd6491f",
    "41587_2024_2511_Tab1_ESM.jpg": "b2673b8e14f8d0c4e12892600620ccd93c6de6f36a112473816057c9d7423387",
    "out_MOESM1_ESM.pdf": "75874bda760405cb98d3712e9319a94fb73838b4a412fd3ba340ddf3b7d6fcb4",
}
ARTICLE_SHA_AS_USED = "accc02ff43f84cf716d56a92b09664cb36506984162d0f5d45773db1c41c2d3f"

P = "gpn-msa-published-20261116"
S_ARTICLE = f"{P}-source-nbt-2025"
S_TAB1_PAGE = f"{P}-source-extended-data-table-1-page"
S_TAB1_IMAGE = f"{P}-source-extended-data-table-1-image"
S_FIG2_PAGE = f"{P}-source-figure-2-page"
S_SUPP = f"{P}-source-supplementary-information"

PREPRINT = "gfm-guides-20261014-gpnmsa-source-biorxiv-v2"
MODEL = "gfm-guides-20261014-gpnmsa-model-gpn-msa"
BENCHMARK = "gfm-guides-20261014-gpnmsa-benchmark-gpn-msa-vep"
DATA = {
    "ClinVar": "gfm-guides-20261014-gpnmsa-data-clinvar-vs-gnomad-common-missense",
    "COSMIC": "gfm-guides-20261014-gpnmsa-data-cosmic-frequent-vs-gnomad-common-missense",
    "OMIM": "gfm-guides-20261014-gpnmsa-data-omim-vs-gnomad-common-regulatory",
    "gnomAD": "gfm-guides-20261014-gpnmsa-data-gnomad-rare-vs-common-ablation-set",
}

ARTICLE_URL = "https://www.nature.com/articles/s41587-024-02511-w"
TAB1_PAGE_URL = f"{ARTICLE_URL}/tables/1"
FIG2_PAGE_URL = f"{ARTICLE_URL}/figures/2"
TAB1_IMAGE_URL = ("https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-024-02511-w"
                  "/MediaObjects/41587_2024_2511_Tab1_ESM.jpg")
SUPP_URL = ("https://static-content.springer.com/esm/art%3A10.1038%2Fs41587-024-02511-w"
            "/MediaObjects/41587_2024_2511_MOESM1_ESM.pdf")

RETRIEVED = "2026-11-16T00:24:00Z"
DATE = "2026-11-16"
EXTRACTOR_NOTE = ("Claude (Opus 5) extraction agent for rewire-benchmark-data issue #226, published "
                  "GPN-MSA batch; extraction only, not a review. Pending an independent "
                  "review-evidence pass.")
FACETS = {"areas": ["dna-genomes"], "contexts": ["research"]}

# Extended Data Table 1 "Ablation study", transcribed from the pinned JPEG.
# Columns: ClinVar mean/max, COSMIC mean/max, OMIM mean/max, gnomAD mean/max.
TAB1 = [
    ("Default", "0.969", "0.969", "0.348", "0.355", "0.124", "0.133", "41.377", "43.118"),
    ("w/o MSA", "0.584", "0.585", "0.012", "0.012", "0.000", "0.000", "2.773", "3.093"),
    ("MSA frequency (no neural net)", "0.950", "0.950", "0.270", "0.270", "0.031", "0.031", "15.122", "15.122"),
    ("Combined phyloP and phastCons", "0.928", "0.928", "0.141", "0.141", "0.039", "0.039", "13.919", "13.919"),
    ("Train on 50% most conserved", "0.963", "0.963", "0.241", "0.257", "0.125", "0.139", "32.116", "35.286"),
    ("Train on 100% of genome", "0.960", "0.961", "0.210", "0.224", "0.120", "0.122", "27.964", "30.717"),
    ("Include closest primates", "0.954", "0.956", "0.214", "0.219", "0.139", "0.156", "24.674", "26.721"),
    ("51 mammals", "0.964", "0.965", "0.323", "0.325", "0.073", "0.076", "41.381", "43.408"),
    ("51 vertebrates", "0.967", "0.967", "0.342", "0.347", "0.101", "0.108", "41.624", "46.792"),
    ("Don’t upweight conserved", "0.967", "0.967", "0.303", "0.309", "0.133", "0.152", "37.094", "39.991"),
    ("Don’t replace non-conserved", "0.966", "0.967", "0.333", "0.340", "0.111", "0.112", "41.853", "45.213"),
    ("Window size = 256", "0.969", "0.969", "0.366", "0.376", "0.119", "0.128", "37.908", "42.957"),
    ("Window size = 64", "0.968", "0.968", "0.340", "0.348", "0.111", "0.119", "37.478", "39.522"),
    ("Window size = 32", "0.967", "0.967", "0.323", "0.328", "0.108", "0.121", "36.664", "38.866"),
    ("Window size = 16", "0.964", "0.965", "0.246", "0.250", "0.095", "0.106", "29.203", "31.623"),
    ("Window size = 8", "0.961", "0.961", "0.188", "0.209", "0.080", "0.086", "21.159", "21.943"),
    ("Window size = 4", "0.942", "0.943", "0.131", "0.155", "0.052", "0.053", "13.457", "14.789"),
]
COLUMNS = [("ClinVar", "mean"), ("ClinVar", "max"), ("COSMIC", "mean"), ("COSMIC", "max"),
           ("OMIM", "mean"), ("OMIM", "max"), ("gnomAD", "mean"), ("gnomAD", "max")]

TAB1_CAPTION = (
    "Performance of three random seeds of each independent ablation on four variant effect "
    "prediction metrics. ClinVar (AUROC): same setting as Fig. 2c . COSMIC (AUPRC): same setting "
    "as Fig. 2e . OMIM (AUPRC): same setting as Fig. 2f . gnomAD (odds ratio): same approach as "
    "Fig. 2g , including all variant types, but subsetting the rare variants to match the number "
    "of common variants. Ablations are detailed in Methods.")

FIG2_PANELS = {
    "c": ("c , Classification of ClinVar pathogenic versus gnomAD common missense variants. "
          "Exact sample size, n = 21,273 versus 15,402."),
    "d": ("d , Classification of ClinVar pathogenic versus ClinVar benign missense variants. "
          "Exact sample size, n = 21,275 versus 26,993."),
    "e": ("e , Classification of COSMIC frequent (frequency > 0.1%) versus gnomAD common missense "
          "variants. Exact sample size, n = 183 versus 15,399."),
    "f": ("f , Classification of OMIM pathogenic versus gnomAD common regulatory variants."),
    "g": ("g , Enrichment of rare (singletons) versus common (MAF > 5%) gnomAD variants in the "
          "tail of deleterious scores"),
}
FIG2_OMIM_N = "Exact sample size, n = 406 versus 2,573,918."
FIG2_GNOMAD_N = "Exact sample size, n = 252,706,195 versus 5,894,721."

SUPP_LISTING = "Supplementary Tables 1–6 and Figs. 1–8."

SUPP_T1 = [("CDS", "0.915", "1.032"), ("5’ UTR", "0.837", "1.646"),
           ("3’ UTR", "0.821", "1.688"), ("Non-exonic", "0.690", "1.978")]
SUPP_T2 = [("CDS", "0.227", "0.680"), ("5’ UTR", "0.177", "0.679"),
           ("3’ UTR", "0.245", "0.603"), ("Non-exonic", "0.268", "0.515")]


def sha(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def plain(path):
    """nature.com markup reduced to the running text, the way the captions were read."""
    html = open(path, encoding="utf-8", errors="replace").read()
    html = re.sub(r"<script.*?</script>", "", html, flags=re.S)
    html = re.sub(r"<style.*?</style>", "", html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", html)
    for entity, char in (("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'),
                         ("&#39;", "'"), ("&nbsp;", " "), ("&rsquo;", "’"),
                         ("&ndash;", "–"), ("&minus;", "−")):
        text = text.replace(entity, char)
    text = re.sub(r"&[a-zA-Z#0-9]+;", " ", text)
    return re.sub(r"\s+", " ", text)


# ------------------------------------------------------------------ artifacts
for name, expected in SHA.items():
    got = sha(os.path.join(ART, name))
    assert got == expected, f"{name}: expected {expected}, got {got}"

article_sha = sha(os.path.join(ART, "nature_article.html"))
print(f"nature_article.html sha256 {article_sha}"
      f"{'  (matches the pinned retrieval)' if article_sha == ARTICLE_SHA_AS_USED else '  (differs from the pinned retrieval; the page is mutable)'}")

article = plain(os.path.join(ART, "nature_article.html"))
tab1_page = plain(os.path.join(ART, "tab1.html"))
fig2_page = plain(os.path.join(ART, "fig2.html"))
supp = open(os.path.join(ART, "moesm1.txt"), encoding="utf-8").read()

assert "Extended Data Table 1 Ablation study" in tab1_page
assert TAB1_CAPTION in tab1_page, "Extended Data Table 1 caption not found verbatim"
for letter, passage in FIG2_PANELS.items():
    assert passage in fig2_page, f"Figure 2 panel {letter} caption not found verbatim"
assert FIG2_OMIM_N in fig2_page and FIG2_GNOMAD_N in fig2_page
assert SUPP_LISTING in article, "Supplementary Information listing not found"
assert "Nat Biotechnol 43 , 1960–1965 (2025)" in article.replace("&#8211;", "–")
assert "A DNA language model based on multispecies alignment predicts the effects of genome-wide variants" in article
assert "https://doi.org/10.1038/s41587-024-02511-w" in supp

# ------------------------------------- published Supplementary Tables 1 and 2 (text layer)
assert "Supplementary Table 1: Held-out accuracy. 39M positions in chromosome 22 were evaluated." in supp
assert ("Supplementary Table 2: Held-out accuracy at sites where ancestral allele differs from "
        "reference allele. 245K") in supp
assert "Supplementary Table 4: Training hyperparameters" in supp, "published Supp Table 4 is the hyperparameter table"
assert "Supplementary Table 5: Best quantiles in each group of variants" in supp

block1 = supp.split("Supplementary Table 1:")[1].split("Supplementary Table 2:")[0]
block2 = supp.split("Supplementary Table 2:")[1].split("Supplementary Table 3:")[0]
for block, rows, label in ((block1, SUPP_T1, "Supplementary Table 1"), (block2, SUPP_T2, "Supplementary Table 2")):
    for region, first, second in rows:
        pattern = re.escape(region) + r"\s+" + re.escape(first) + r"\s+" + re.escape(second)
        assert re.search(pattern, block), f"{label} row {region} not found as printed"

# ---------------------------------------------------- stored bioRxiv v2 results
stored = {}
other = []
for name in sorted(os.listdir(os.path.join(STORE, "data", "evidence", "results"))):
    for line in open(os.path.join(STORE, "data", "evidence", "results", name), encoding="utf-8"):
        record = json.loads(line)
        if PREPRINT not in record.get("source_ids", []):
            continue
        locator = record["attributes"].get("source_locator", "")
        match = re.match(r"Supplementary Table 4 \(PDF page 23\), row '(.*)', column '(.*)' / '(.*)'", locator)
        if match:
            stored[(match.group(1), match.group(2), match.group(3))] = (
                record["id"], record["attributes"]["printed_value"])
        else:
            other.append((record["id"], record["attributes"]["printed_value"], locator))

assert len(stored) + len(other) == 138, f"expected 138 stored results on the preprint, got {len(stored) + len(other)}"
assert len(stored) == 136, f"expected 136 stored Supplementary Table 4 cells, got {len(stored)}"
assert len(other) == 2, "expected the two DMS TADBP results outside the table"

# ---------------------------------------------------------------- comparison
differ = []
with open(os.path.join(OUT, "extract", "comparison.tsv"), "w", encoding="utf-8") as handle:
    handle.write("stored_result_id\trow\tcolumn\tseed_aggregate\tstored_value_biorxiv_v2\t"
                 "published_value_extended_data_table_1\tsame_protocol\tdiffers\n")
    for row in TAB1:
        label, values = row[0], row[1:]
        for (column, aggregate), published in zip(COLUMNS, values):
            key = (label, column, aggregate)
            assert key in stored, f"no stored result for {key}"
            result_id, stored_value = stored[key]
            same = stored_value == published
            if not same:
                differ.append((result_id, stored_value, published))
            handle.write(f"{result_id}\t{label}\t{column}\t{aggregate}\t{stored_value}\t"
                         f"{published}\tyes\t{'no' if same else 'YES'}\n")
    for result_id, value, locator in sorted(other):
        handle.write(f"{result_id}\tDMS TADBP (Results text)\t-\t-\t{value}\t"
                     f"not retrieved\tunknown\tnot compared\n")

print(f"compared {len(stored)} stored values against Extended Data Table 1; {len(differ)} differ")
for entry in differ:
    print("  differs:", entry)

# ---------------------------------------------------------------- records
records = []


def review(method, method_note, artifact_sha256, retrieval_url, note):
    return {"method": method, "method_note": method_note, "reviewer": ["claude"],
            "reviewer_note": EXTRACTOR_NOTE, "date": DATE, "artifact_sha256": artifact_sha256,
            "retrieval_url": retrieval_url, "note": note}


def add(record):
    records.append(record)


add({
    "id": S_ARTICLE, "kind": "source",
    "name": ("A DNA language model based on multispecies alignment predicts the effects of "
             "genome-wide variants (Nature Biotechnology 2025)"),
    "description": ("Peer-reviewed version of the GPN-MSA paper (Benegas, Albors, Aw, Ye and Song), "
                    "retrieved as the publisher's article page."),
    "status": "needs_review", "facets": FACETS, "source_ids": [],
    "links": [{"relation": "companion_of", "target_id": PREPRINT}],
    "attributes": {
        "url": ARTICLE_URL, "artifact_url": ARTICLE_URL,
        "doi": "10.1038/s41587-024-02511-w",
        "version": "Version of record, Nature Biotechnology 43, 1960-1965 (2025); published online 2025-01-02",
        "retrieved_at": RETRIEVED, "artifact_sha256": ARTICLE_SHA_AS_USED,
        "publication_status": "peer_reviewed",
        "licence": ("Springer Nature holds exclusive rights under a publishing agreement; not open "
                    "access. No copy is archived in this repository."),
        "media_type": "text/html", "venue": "Nature Biotechnology", "year": 2025,
        "source_locator": ("Abstract; Extended Data figure captions; Data availability; Code "
                           "availability; Supplementary information listing; citation block"),
        "hash_scope": ("SHA-256 of the page bytes as downloaded 2026-11-16T00:24Z. The page is "
                       "mutable: two retrievals seconds apart gave different bytes, because "
                       "nature.com varies advertising and session markup. The hash describes one "
                       "retrieval. The passages this batch uses are asserted verbatim by "
                       "extract/build_gpn_msa_published.py instead."),
        "limitations": [
            ("Not open access. The Results and Methods body was not retrieved: only the abstract, "
             "the figure and Extended Data captions, Data availability, Code availability, the "
             "supplementary listing and the citation block are served without a subscription."),
            ("Europe PMC, the PMC ID converter, PMC eLink, Unpaywall and OpenAlex index no open "
             "copy of this version; every open location they list is the bioRxiv preprint."),
            ("Figure 1, Figure 2 and Extended Data Figures 1 to 8 print no numbers in their "
             "captions beyond sample sizes, and no Source Data file is published."),
        ],
        "review": review(["source-hash-verification", "transcription"],
                         "Page retrieved with curl and reduced to running text; the passages used are asserted verbatim.",
                         ARTICLE_SHA_AS_USED, ARTICLE_URL,
                         "Extraction pass 2026-11-16. The body is paywalled; nothing was taken from it."),
    },
})

add({
    "id": S_TAB1_PAGE, "kind": "source",
    "name": "Extended Data Table 1 (Ablation study) page, GPN-MSA Nature Biotechnology 2025",
    "description": ("Publisher's page for Extended Data Table 1 of the GPN-MSA paper, which carries "
                    "the table caption as text."),
    "status": "needs_review", "facets": FACETS, "source_ids": [],
    "links": [{"relation": "companion_of", "target_id": S_ARTICLE}],
    "attributes": {
        "url": TAB1_PAGE_URL, "artifact_url": TAB1_PAGE_URL,
        "doi": "10.1038/s41587-024-02511-w",
        "version": "Version of record, Nature Biotechnology 43, 1960-1965 (2025)",
        "retrieved_at": RETRIEVED, "artifact_sha256": SHA["tab1.html"],
        "publication_status": "peer_reviewed",
        "licence": ("Springer Nature holds exclusive rights under a publishing agreement; not open "
                    "access. No copy is archived in this repository."),
        "media_type": "text/html", "venue": "Nature Biotechnology", "year": 2025,
        "source_locator": "Extended Data Table 1 title and caption",
        "hash_scope": ("SHA-256 of the page bytes as downloaded 2026-11-16T00:24Z. Two retrievals "
                       "gave identical bytes, unlike the main article page."),
        "limitations": ["The page carries the caption only. The table body is served as a separate "
                        "raster image, registered as "
                        + S_TAB1_IMAGE + "."],
        "review": review(["source-hash-verification", "transcription"],
                         "Page re-downloaded; hash matched; caption asserted verbatim.",
                         SHA["tab1.html"], TAB1_PAGE_URL,
                         "Extraction pass 2026-11-16."),
    },
})

add({
    "id": S_TAB1_IMAGE, "kind": "source",
    "name": "Extended Data Table 1 (Ablation study) image, GPN-MSA Nature Biotechnology 2025",
    "description": ("Raster image in which the GPN-MSA paper publishes the body of Extended Data "
                    "Table 1, the ablation study."),
    "status": "needs_review", "facets": FACETS, "source_ids": [],
    "links": [{"relation": "companion_of", "target_id": S_ARTICLE}],
    "attributes": {
        "url": TAB1_PAGE_URL, "artifact_url": TAB1_IMAGE_URL,
        "doi": "10.1038/s41587-024-02511-w",
        "version": "Version of record, Nature Biotechnology 43, 1960-1965 (2025)",
        "retrieved_at": RETRIEVED, "artifact_sha256": SHA["41587_2024_2511_Tab1_ESM.jpg"],
        "publication_status": "peer_reviewed",
        "licence": ("Springer Nature holds exclusive rights under a publishing agreement; not open "
                    "access. No copy is archived in this repository."),
        "media_type": "image/jpeg", "venue": "Nature Biotechnology", "year": 2025,
        "source_locator": "Extended Data Table 1, all 17 rows by the ClinVar, COSMIC, OMIM and gnomAD column groups",
        "hash_scope": ("SHA-256 of the JPEG as downloaded 2026-11-16T00:24Z from static-content."
                       "springer.com; two retrievals gave identical bytes. The copy embedded in the "
                       "table page is a 638-pixel-wide derivative of the same object; the full-size "
                       "original used here is 1594 by 949 pixels."),
        "limitations": [
            ("The table is published only as an image. It has no text layer, so npm run batch -- "
             "check-values cannot read it and the values can only be read by eye."),
            ("The 136 values were read from this image by the extraction agent and compared cell by "
             "cell with the stored bioRxiv v2 values in extract/comparison.tsv. A reviewer should "
             "re-read the image independently rather than treat the transcription as parsed."),
        ],
        "review": review(["source-hash-verification", "rendered-source-visual-check", "transcription"],
                         ("The JPEG was re-downloaded and its hash matched. Its 136 values were read "
                          "visually and written into extract/build_gpn_msa_published.py as TAB1, then "
                          "every row was read a second time from the image resampled to twice its size "
                          "and cropped into three overlapping bands; the second reading agreed with "
                          "TAB1 in every cell. No OCR tool was available in the environment "
                          "(tesseract is not installed), so there is no machine reading."),
                         SHA["41587_2024_2511_Tab1_ESM.jpg"], TAB1_IMAGE_URL,
                         ("Extraction pass 2026-11-16. The image was viewed before the stored "
                          "preprint values were loaded, but the transcription into digits was "
                          "written with the stored values in view, so it is not independent of them. "
                          "The agreement is evidence, not verification: a reviewer must re-read the "
                          "image without the stored values to hand.")),
    },
})

add({
    "id": S_FIG2_PAGE, "kind": "source",
    "name": "Figure 2 (VEP results) page, GPN-MSA Nature Biotechnology 2025",
    "description": ("Publisher's page for Figure 2 of the GPN-MSA paper, which carries the full "
                    "panel caption with the sample size of each comparison."),
    "status": "needs_review", "facets": FACETS, "source_ids": [],
    "links": [{"relation": "companion_of", "target_id": S_ARTICLE}],
    "attributes": {
        "url": FIG2_PAGE_URL, "artifact_url": FIG2_PAGE_URL,
        "doi": "10.1038/s41587-024-02511-w",
        "version": "Version of record, Nature Biotechnology 43, 1960-1965 (2025)",
        "retrieved_at": RETRIEVED, "artifact_sha256": SHA["fig2.html"],
        "publication_status": "peer_reviewed",
        "licence": ("Springer Nature holds exclusive rights under a publishing agreement; not open "
                    "access. No copy is archived in this repository."),
        "media_type": "text/html", "venue": "Nature Biotechnology", "year": 2025,
        "source_locator": "Figure 2 caption, panels a to h",
        "hash_scope": ("SHA-256 of the page bytes as downloaded 2026-11-16T00:24Z. Two retrievals "
                       "gave identical bytes."),
        "limitations": ["The figure itself prints no numbers; only the caption's sample sizes were used."],
        "review": review(["source-hash-verification", "transcription"],
                         "Page re-downloaded; hash matched; the panel captions used are asserted verbatim.",
                         SHA["fig2.html"], FIG2_PAGE_URL, "Extraction pass 2026-11-16."),
    },
})

add({
    "id": S_SUPP, "kind": "source",
    "name": "Supplementary Information, GPN-MSA Nature Biotechnology 2025",
    "description": ("Supplementary Information of the published GPN-MSA paper: Supplementary Tables "
                    "1 to 6 and Supplementary Figures 1 to 8."),
    "status": "needs_review", "facets": FACETS, "source_ids": [],
    "links": [{"relation": "companion_of", "target_id": S_ARTICLE}],
    "attributes": {
        "url": ARTICLE_URL, "artifact_url": SUPP_URL,
        "doi": "10.1038/s41587-024-02511-w",
        "version": "Version of record, Nature Biotechnology 43, 1960-1965 (2025); 12 pages",
        "retrieved_at": RETRIEVED, "artifact_sha256": SHA["out_MOESM1_ESM.pdf"],
        "publication_status": "peer_reviewed",
        "licence": ("Springer Nature holds exclusive rights under a publishing agreement; not open "
                    "access. No copy is archived in this repository."),
        "media_type": "application/pdf", "venue": "Nature Biotechnology", "year": 2025,
        "source_locator": "Supplementary Tables 1 to 6 (pages 1 to 4); Supplementary Figures 1 to 8 (pages 5 to 12)",
        "hash_scope": ("SHA-256 of the PDF as downloaded 2026-11-16T00:24Z; two retrievals gave "
                       "identical bytes. The text layer used for the table checks is regenerated "
                       "with pdftotext -layout."),
        "limitations": [
            ("The supplement carries no ablation study: in the published version that table is "
             "Extended Data Table 1. Published Supplementary Table 4 is the training hyperparameter "
             "table, which is Supplementary Table 5 in the preprint."),
            ("The only numeric result tables are Supplementary Tables 1 and 2 (held-out accuracy and "
             "median perplexity on chromosome 22). They print the same 16 values as the preprint and "
             "are not extracted as results in this batch."),
            "Supplementary Figures 1 to 8 print no numbers and were not read.",
        ],
        "review": review(["source-hash-verification", "pdf-text-parse"],
                         ("PDF re-downloaded and its hash matched; Supplementary Tables 1 and 2 were "
                          "parsed from the pdftotext -layout text layer with their row labels asserted."),
                         SHA["out_MOESM1_ESM.pdf"], SUPP_URL, "Extraction pass 2026-11-16."),
    },
})

# ---------------------------------------------------------------- claims
image_review = review(
    ["rendered-source-visual-check", "transcription", "source-hash-verification"],
    ("All 136 cells of Extended Data Table 1 were read from the pinned JPEG and compared, cell by "
     "cell, with the 136 stored results that cite the bioRxiv v2 Supplementary Table 4. The "
     "comparison is extract/comparison.tsv, produced by extract/build_gpn_msa_published.py."),
    SHA["41587_2024_2511_Tab1_ESM.jpg"], TAB1_IMAGE_URL,
    ("No value differs. The transcription was written with the stored values in view, so it is not "
     "independent of them, and the table has no text layer for a parser to check. The reviewer must "
     "re-read the image without the stored values to hand."))

add({
    "id": f"{P}-claim-ablation-values-unchanged", "kind": "claim",
    "name": "published_version_values_ablation_table: GPN-MSA",
    "description": "Comparison of a stored preprint table with the same table in the published version.",
    "status": "needs_review", "facets": FACETS,
    "source_ids": [S_TAB1_IMAGE, S_TAB1_PAGE, PREPRINT],
    "links": [{"relation": "subject", "target_id": PREPRINT}],
    "attributes": {
        "field": "published_version_values_ablation_table",
        "value": ("The ablation study the store holds from bioRxiv v2 Supplementary Table 4 is "
                  "reprinted unchanged in the peer-reviewed version as Extended Data Table 1. All "
                  "136 printed cells (17 ablation rows by ClinVar AUROC, COSMIC AUPRC, OMIM AUPRC "
                  "and gnomAD odds ratio, each as mean and maximum over three random seeds) have "
                  "the same value and the same number of decimal places in both versions. The "
                  "protocols are the same: the caption of each version describes the same four "
                  "settings, and the only change is which Figure 2 panel letters it cites. No "
                  "correction is needed to any stored result."),
        "source_locator": ("Extended Data Table 1 (image artifact), all rows and columns; caption on "
                           "the Extended Data Table 1 page"),
        "review": image_review,
    },
})

add({
    "id": f"{P}-claim-held-out-accuracy-unchanged", "kind": "claim",
    "name": "published_version_values_held_out_accuracy: GPN-MSA",
    "description": "Comparison of the preprint's held-out accuracy tables with the published version's.",
    "status": "needs_review", "facets": FACETS, "source_ids": [S_SUPP, PREPRINT],
    "links": [{"relation": "subject", "target_id": PREPRINT}],
    "attributes": {
        "field": "published_version_values_held_out_accuracy",
        "value": ("Supplementary Tables 1 and 2 (held-out accuracy and median perplexity on "
                  "chromosome 22, and accuracy at sites where the ancestral allele differs from the "
                  "reference) print the same 16 values in the published Supplementary Information as "
                  "in bioRxiv v2, over the same four regions (CDS, 5' UTR, 3' UTR, non-exonic) and "
                  "the same stated position counts (39M and 245K). Neither version's values are in "
                  "the store: they are language-model accuracy figures, left out of the earlier "
                  "batch by scope."),
        "source_locator": "Supplementary Tables 1 and 2 (page 1 of the Supplementary Information)",
        "review": review(["pdf-text-parse", "source-hash-verification"],
                         ("Both tables parsed from the pdftotext -layout text layer of the pinned "
                          "Supplementary Information with their row labels asserted, and compared "
                          "with the same tables in the pinned bioRxiv v2 text layer."),
                         SHA["out_MOESM1_ESM.pdf"], SUPP_URL,
                         "No value differs."),
    },
})

add({
    "id": f"{P}-claim-table-numbering", "kind": "claim",
    "name": "published_version_table_numbering: GPN-MSA variant effect prediction evaluation",
    "description": "Where each table of the preprint is printed in the published version.",
    "status": "needs_review", "facets": FACETS, "source_ids": [S_SUPP, S_TAB1_PAGE, S_ARTICLE, PREPRINT],
    "links": [{"relation": "subject", "target_id": BENCHMARK}],
    "attributes": {
        "field": "published_version_table_numbering",
        "value": ("Table numbering changed between the versions. Preprint Supplementary Tables 1, 2 "
                  "and 3 keep their numbers. The ablation study, preprint Supplementary Table 4, "
                  "became Extended Data Table 1. Preprint Supplementary Table 5 (training "
                  "hyperparameters) became published Supplementary Table 4, and preprint "
                  "Supplementary Table 6 (functional annotations) stayed Supplementary Table 6. "
                  "Published Supplementary Table 5, the best score quantiles for summarising variant "
                  "scores into gene-level scores, has no counterpart in the preprint. A stored "
                  "result whose locator names 'Supplementary Table 4' therefore points at the "
                  "ablation study in the preprint and at the hyperparameter table in the published "
                  "version."),
        "source_locator": ("Supplementary Information contents and Supplementary Tables 1 to 6; "
                           "Extended Data Table 1 page; article page, Supplementary information section"),
        "review": review(["pdf-text-parse", "transcription", "source-hash-verification"],
                         ("Table titles read from the pinned Supplementary Information text layer and "
                          "from the Extended Data Table 1 page, and compared with the pinned bioRxiv "
                          "v2 text layer."),
                         SHA["out_MOESM1_ESM.pdf"], SUPP_URL,
                         "Published Supplementary Table 5 is a setting, not a measured result, and is not extracted."),
    },
})

add({
    "id": f"{P}-claim-figure-2-panels", "kind": "claim",
    "name": "published_version_figure_panels: GPN-MSA variant effect prediction evaluation",
    "description": "How the Figure 2 panels the ablation caption cites changed between the versions.",
    "status": "needs_review", "facets": FACETS, "source_ids": [S_FIG2_PAGE, S_TAB1_PAGE, PREPRINT],
    "links": [{"relation": "subject", "target_id": BENCHMARK}],
    "attributes": {
        "field": "published_version_figure_panels",
        "value": ("Published Figure 2 has eight panels, a to h, where bioRxiv v2 Figure 2 has seven, "
                  "a to g. The published version inserts a new panel d, ClinVar pathogenic versus "
                  "ClinVar benign missense variants, which shifts COSMIC, OMIM, gnomAD and DepMap "
                  "from preprint panels d, e, f and g to published panels e, f, g and h. The "
                  "ablation caption follows the change: bioRxiv v2 Supplementary Table 4 cites "
                  "Figure 2a, 2b, 2c and 2d for ClinVar, COSMIC, OMIM and gnomAD, which are the "
                  "wrong panels in that version, while published Extended Data Table 1 cites Fig. "
                  "2c, 2e, 2f and 2g, which are the right ones. The protocols themselves did not "
                  "change; the preprint's caption pointers were wrong and the published caption is "
                  "correct."),
        "source_locator": ("Figure 2 caption, panels a to h; Extended Data Table 1 caption"),
        "review": review(["transcription", "source-hash-verification"],
                         ("Both captions read from the pinned publisher pages, with the panel "
                          "passages asserted verbatim, and compared with the Figure 2 and "
                          "Supplementary Table 4 captions in the pinned bioRxiv v2 text layer."),
                         SHA["fig2.html"], FIG2_PAGE_URL,
                         ("This settles the off-by-two that "
                          "data/omics/gfm-guides-20261014-gpnmsa raised as a question for its "
                          "reviewer: it was an error in the preprint caption, fixed on publication.")),
    },
})

SIZES = [
    ("clinvar", "ClinVar", DATA["ClinVar"],
     "n = 21,273 ClinVar pathogenic versus 15,402 gnomAD common missense variants",
     "Figure 2 caption, panel c"),
    ("cosmic", "COSMIC", DATA["COSMIC"],
     "n = 183 COSMIC frequent versus 15,399 gnomAD common missense variants",
     "Figure 2 caption, panel e"),
    ("omim", "OMIM", DATA["OMIM"],
     "n = 406 OMIM pathogenic versus 2,573,918 gnomAD common regulatory variants",
     "Figure 2 caption, panel f"),
]
for slug, label, target, value, locator in SIZES:
    add({
        "id": f"{P}-claim-sample-size-{slug}", "kind": "claim",
        "name": f"denominator: {label} set of the GPN-MSA ablation",
        "description": "Sample size the published version prints for a set the preprint left uncounted.",
        "status": "needs_review", "facets": FACETS, "source_ids": [S_FIG2_PAGE, S_TAB1_PAGE],
        "links": [{"relation": "subject", "target_id": target}],
        "attributes": {
            "field": "denominator",
            "value": (f"The published version prints {value}. The preprint prints no counts, so the "
                      f"stored dataset record carries missing_metadata.denominator with reason "
                      f"'unreported'. Extended Data Table 1 states that the ablation's {label} "
                      f"column uses the same setting as this panel, so the count applies to the "
                      f"ablation results as well."),
            "source_locator": locator,
            "review": review(["transcription", "source-hash-verification"],
                             "Caption passage asserted verbatim in the pinned Figure 2 page.",
                             SHA["fig2.html"], FIG2_PAGE_URL,
                             ("New in the published version: Nature prints exact sample sizes that "
                              "the preprint caption does not. Updating the stored dataset record is "
                              "a reviewer decision, not an extractor edit.")),
        },
    })

add({
    "id": f"{P}-claim-sample-size-gnomad", "kind": "claim",
    "name": "denominator: gnomAD ablation set of the GPN-MSA ablation",
    "description": "What the published version prints about the size of the gnomAD ablation set.",
    "status": "needs_review", "facets": FACETS, "source_ids": [S_FIG2_PAGE, S_TAB1_PAGE],
    "links": [{"relation": "subject", "target_id": DATA["gnomAD"]}],
    "attributes": {
        "field": "denominator",
        "value": ("The published version prints n = 252,706,195 rare versus 5,894,721 common gnomAD "
                  "variants for Figure 2g. That is the full set, not the ablation set: Extended Data "
                  "Table 1 says its gnomAD column uses the same approach as Fig. 2g but subsets the "
                  "rare variants to match the number of common variants, and neither version prints "
                  "the size of that subset. The ablation set's size stays unreported."),
        "source_locator": "Figure 2 caption, panel g; Extended Data Table 1 caption",
        "review": review(["transcription", "source-hash-verification"],
                         "Both caption passages asserted verbatim in the pinned publisher pages.",
                         SHA["fig2.html"], FIG2_PAGE_URL,
                         "Recorded so that the Figure 2g counts are not read as the ablation set's counts."),
    },
})

with open(os.path.join(OUT, "batch.jsonl"), "w", encoding="utf-8") as handle:
    for record in records:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=False) + "\n")

kinds = {}
for record in records:
    kinds[record["kind"]] = kinds.get(record["kind"], 0) + 1
print("records:", kinds, "total", len(records))
