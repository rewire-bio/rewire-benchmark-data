"""Deterministic extraction of the targeted-panel cfDNA fragmentomics metric comparison in Helzer et al. 2025.

Usage: python3 -I extract_helzer2025.py <download-dir> <batch-dir>

Reads two pinned artifacts:
  - the article, PMC12521513 full-text JATS XML (Nature Communications 2025, 10.1038/s41467-025-64153-z)
  - Supplementary Information PDF (41467_2025_64153_MOESM1_ESM.pdf), through its text layer
    (pdftotext -layout, poppler 26.08.0, written beside it as MOESM1.txt)
Every cell of the two AUROC tables is extracted: the GRAIL-cohort table (4 gene panels x 13 metrics x 4 phenotypes and
the mean) and the UW-cohort table (4 gene panels x 13 or 14 metrics x 9 phenotypes and the mean). Asserts the header
labels, the metric labels in each panel block, the panel labels printed beside each block, that each 'Mean AUROC'
equals the mean of its row to the printed rounding, and the article sentences that fix the column order.
Writes batch.jsonl, claims.csv and use-case-links.json.

Corrections from the independent review (docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md) are applied here
and marked with their review item (A2, H1 to H3); B.finalize applies the review to every record.
"""
import os, re, sys
import xml.etree.ElementTree as ET
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (Batch, UC_FRAG, Q_FRAG, sha, expect)  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
B = Batch("ctdnalit-20261011-helzer2025", "2026-10-11")
P = B.P
XML, PDF, TXT = f"{DL}/helzer/PMC12521513.xml", f"{DL}/helzer/41467_2025_64153_MOESM1_ESM.pdf", f"{DL}/helzer/MOESM1.txt"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12521513/fullTextXML"
PDF_URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41467-025-64153-z/MediaObjects/41467_2025_64153_MOESM1_ESM.pdf"
S_ART, S_SI = f"{P}-source-article", f"{P}-source-supplementary-information"
SRC = [S_ART, S_SI]

# ---------------------------------------------------------------- article checks
root = ET.parse(XML).getroot()
FLAT = " ".join(" ".join("".join(p.itertext()).split()) for p in root.iter("p"))
for frag in (
        "normalized fragment read depth across all exons provided the best average performance for predicting cancer types and subtypes with an average AUROC of 0.943 and a range of 0.873 for NSCLC to 0.986 for healthy samples (Fig. 2; Table S1)",
        "First exon (E1) depth yielded an average AUROC of 0.930 and a range of 0.838 for NSCLC to 0.989 for healthy samples",
        "full gene depth (combining all exons from one gene into a single feature) yielded an average AUROC of 0.919 with a range of 0.828 for NSCLC to 0.993 for NEPC (Table S1)",
        "In the GRAIL cohort, we similarly found that normalized fragment read depth across all exons was the best performing metric with an average AUROC of 0.964 and a range from 0.914 for lung cancer to 1.000 for healthy samples (Fig. 3; Table S2)",
        "the top-performing metric for SCLC in the UW cohort was MDS across all exons with an average AUROC of 0.888",
        "an in-house cohort collected at the University of Wisconsin (UW) comprising 431 samples (38 bladder cancer, 71 ER-positive breast cancer, 29 ER-negative breast cancer, 15 neuroendocrine prostate cancer (NEPC), 144 prostate adenocarcinoma, 44 renal cell carcinoma (RCC), 16 small cell lung cancer (SCLC), 47 non-small cell lung cancer (NSCLC), and 27 healthy i.e. non-cancer donors)",
        "a publicly available dataset from Razavi et al. comprising 198 samples (48 breast, 49 lung, 54 prostate, 47 healthy i.e. non-cancer; cancer subtype information not available)",
        "a multinomial logistic regression using the generalized linear model with elastic net penalty (GLMnet) was used for cancer type and cancer vs. healthy predictions",
        "10-fold cross-validation was used for training and validation, with 25 unique seeds resulting in 25 unique sets of 10 folds",
        "Folds were set first so that the same folds could be used",
        "The medians across these replicates are reported.",
        "We recently published on the utility of fragmentomics from such targeted panels for cancer phenotyping, with a focus on the entropy in the first exons (E1) of genes in these panels",
        "It is important to note that the goal of this study is not to produce and assess performance of a “locked” prediction model."):
    expect(frag in FLAT, True, f"article sentence: {frag[:60]}")

# ---------------------------------------------------------------- supplementary tables
lines = open(TXT, encoding="utf-8").read().splitlines()
cap1 = [i for i, l in enumerate(lines) if l.startswith("Table S1. Summary table of AUROC scores for each feature and phenotype in the GRAIL cohort.")]
cap2 = [i for i, l in enumerate(lines) if l.startswith("Table S2. Summary table of AUROC scores for each feature and phenotype in the UW cohort.")]
expect((len(cap1), len(cap2)), (1, 1), "table captions")
hdr1 = [i for i, l in enumerate(lines) if l.split() == ["Feature", "Table", "Gene", "Panel", "Breast", "Lung", "Normal", "Prostate", "AUROC"]]
expect(len(hdr1), 1, "GRAIL table header")
expect(lines[hdr1[0] - 1].strip(), "Mean", "GRAIL table header 'Mean'")
hdr2 = [i for i in range(cap2[0] - 70, cap2[0]) if lines[i].split() == ["Bladder", "ERneg", "ERpos", "NEPC", "NSCLC", "Normal", "SCLC"]]
expect(len(hdr2), 1, "UW table header")
expect(" ".join(" ".join(lines[i].split()) for i in range(hdr2[0] - 2, hdr2[0] + 4)).split(),
       ["Prostate", "Mean", "Bladder", "ERneg", "ERpos", "NEPC", "NSCLC", "Normal", "SCLC", "Gene", "Panel", "RCC", "AUROC", "Feature"],
       "UW table header layout")
COLS_GRAIL = ["Breast", "Lung", "Normal", "Prostate"]
COLS_UW = ["Bladder", "ERneg", "ERpos", "NEPC", "NSCLC", "Normal", "Prostate", "RCC", "SCLC"]  # order fixed by the article sentences above
FEATS = ["All Exons Depth", "E1 Depth", "Full Gene Depth", "All Exons SE", "E1 SE", "All Exons MDS", "E1 MDS",
         "All Exons Small Fragments", "E1 Small Fragments", "Fragment Bins", "TFBS Entropy", "ATAC Entropy", "All Combined", "Griffin"]
NUM = re.compile(r"^\s+(" + "|".join(re.escape(f) for f in sorted(FEATS, key=len, reverse=True)) + r")\b(.*?)((?:\s+\d\.\d{3})+)\s*$")


def parse(start, end, ncols):
    rows, side = [], []
    for i in range(start, end):
        m = NUM.match(lines[i])
        if m:
            vals = m.group(3).split()
            expect(len(vals), ncols, f"line {i + 1} value count")
            rows.append((i + 1, m.group(1), m.group(2).strip(), vals))
        elif lines[i].strip():
            side.append((i + 1, lines[i].strip()))
    return rows, side


PANELS = ["Full panel", "FoundationOne Liquid CDx", "Guardant360 CDx", "Tempus xF"]
PKEY = {"Full panel": "full", "FoundationOne Liquid CDx": "foundationone", "Guardant360 CDx": "guardant360", "Tempus xF": "tempus-xf"}
g_rows, g_side = parse(hdr1[0] + 1, cap1[0], 5)
u_rows, u_side = parse(hdr2[0] + 4, cap2[0], 10)
expect(len(g_rows), 52, "GRAIL table rows")
expect(len(u_rows), 53, "UW table rows")
BLOCKS = {"grail": [g_rows[0:13], g_rows[13:26], g_rows[26:39], g_rows[39:52]],
          "uw": [u_rows[0:14], u_rows[14:27], u_rows[27:40], u_rows[40:53]]}
for cohort, blocks in BLOCKS.items():
    for k, blk in enumerate(blocks):
        want = FEATS if (cohort, k) == ("uw", 0) else FEATS[:-1]
        expect(sorted(r[1] for r in blk), sorted(want), f"{cohort} {PANELS[k]} metric labels")
# panel labels printed in the table body (inline or on the line between rows)
GRAIL_LABELS = {"GRAIL": 0, "FoundationOne": 1, "Liquid CDx": 1, "Guardant360": 2, "CDx": 2, "Tempus xF": 3}
UW_LABELS = {"UW": 0, "Foundation": 1, "One CDx": 1, "Guardant360": 2, "CDx": 2, "Tempus xF": 3}


def check_labels(rows, side, blocks, labels, cohort):
    first = [blk[0][0] for blk in blocks] + [10 ** 9]
    seen = set()
    for ln, text in [(r[0], r[2]) for r in rows if r[2]] + side:
        if text in ("", "Gene", "Panel", "Feature"):
            continue
        k = max(j for j in range(4) if first[j] - 2 <= ln) if ln >= first[0] - 2 else None
        expect(text in labels and labels[text] == k, True, f"{cohort} panel label {text!r} at line {ln}")
        seen.add(k)
    expect(seen, {0, 1, 2, 3}, f"{cohort} panel labels present")


check_labels(g_rows, [s for s in g_side], BLOCKS["grail"], GRAIL_LABELS, "GRAIL")
check_labels(u_rows, [s for s in u_side if s[1] not in ("Gene", "Panel", "Feature")], BLOCKS["uw"], UW_LABELS, "UW")
for cohort, blocks in BLOCKS.items():
    for blk in blocks:
        for ln, label, _, vals in blk:
            ph = [Decimal(v) for v in vals[:-1]]
            mean = sum(ph) / len(ph)
            expect(abs(mean - Decimal(vals[-1])) <= Decimal("0.0015"), True, f"{cohort} line {ln} {label} mean AUROC")

# ---------------------------------------------------------------- sources
B.source(S_ART, "Analysis of cfDNA fragmentomics metrics and commercial targeted sequencing panels",
         "Primary source retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1038/s41467-025-64153-z", "artifact_url": XML_URL,
          "version": "Nature Communications 16, published online 2025-10-14; Europe PMC full-text JATS XML of PMC12521513",
          "retrieved_at": "2026-10-11T21:40:59Z", "artifact_sha256": sha(XML), "doi": "10.1038/s41467-025-64153-z",
          "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml",
          "source_locator": ("Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> "
                             "element in document order in this JATS XML, front matter included."),  # review A2
          "archive_sha256": sha(f"{BATCH}/artifacts/helzer2025-article.xml.gz"),
          "archive_note": "gzip -n -9 copy of the exact bytes in artifacts/helzer2025-article.xml.gz (CC BY 4.0)",
          "scope_note": ("The authors (University of Wisconsin) previously published first-exon fragment-size entropy on targeted "
                         "panels (their reference 19) and here re-implement other groups' whole-genome fragmentomic metrics on panel "
                         "exons. They state that the study compares metrics and does not produce a locked prediction model.")})
B.source(S_SI, "Helzer et al. 2025, Supplementary Information (Figures S1-S7, Tables S1-S2)",
         "Supplementary PDF retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1038/s41467-025-64153-z", "artifact_url": PDF_URL,
          "version": "41467_2025_64153_MOESM1_ESM.pdf, publisher supplementary file", "retrieved_at": "2026-10-11T21:41:25Z",
          "artifact_sha256": sha(PDF), "doi": "10.1038/s41467-025-64153-z", "publication_status": "peer_reviewed",
          "licence": "CC-BY-4.0", "media_type": "application/pdf",
          "source_locator": "Tables S1 and S2 (pages after Figure S7); per-result locators on each result",
          "retrieval_note": "The same bytes are served inside the Europe PMC supplementaryFiles bundle for PMC12521513 (checked 2026-10-11T21:41:00Z).",
          "archive_note": "Not archived: the 4.5 MB PDF is a stable publisher object pinned by hash.",
          "extraction_method": "pdftotext -layout (poppler 26.08.0) text layer, parsed by extract/extract_helzer2025.py"})

# ---------------------------------------------------------------- datasets, methods, configurations
D_G, D_U = f"{P}-data-grail-razavi2019", f"{P}-data-uw"
B.rec(D_G, "dataset", "Razavi et al. 2019 GRAIL targeted cfDNA cohort as used by Helzer et al. 2025 (198 samples)",
      "Public cfDNA targeted-panel sequencing of 48 breast, 49 lung and 54 prostate cancers and 47 non-cancer donors (508-gene GRAIL panel, about 2.0 Mb, >60,000x).", SRC,
      attributes={"version": "Razavi et al. 2019 (Nature Medicine) GRAIL panel data, as reanalysed by Helzer et al. 2025",
                  "total": 198, "positives": 151, "negatives": 47,
                  "population": "48 breast, 49 lung and 54 prostate cancers (metastatic) and 47 healthy donors; cancer subtypes not available",
                  "assay": "Hybrid-capture targeted sequencing of cfDNA, 508 genes",
                  "scope_note": "Public data generated by GRAIL for Razavi et al. 2019; the Helzer et al. authors did not generate it.",
                  "source_locator": "Results P7; Figure S1"})
B.rec(D_U, "dataset", "University of Wisconsin targeted cfDNA cohort (431 samples)",
      "In-house cfDNA cohort of metastatic cancers and healthy donors sequenced on a custom 822-gene exon panel (about 2.4 Mb, mean 3,038x).", SRC,
      attributes={"version": "Helzer et al. 2025 UW cohort (the 2023 cohort plus 111 added samples)", "total": 431, "positives": 404, "negatives": 27,
                  "population": "38 bladder, 71 ER-positive and 29 ER-negative breast, 15 NEPC, 144 prostate adenocarcinoma, 44 RCC, 16 SCLC and 47 NSCLC cancers, and 27 healthy donors",
                  "assay": "Hybrid-capture targeted sequencing of cfDNA, custom 822-gene exon panel, UMI deduplicated",
                  "scope_note": "Metastatic patients and two clinical trials (NCT03090165, NCT03725761); healthy blood bought from the UWCCC biobank.",
                  "source_locator": "Results P7; Methods P21-P22"})
METRICS = {  # label: (key, name, description, origin, citation)
    "All Exons Depth": ("all-exons-depth", "Normalised fragment read depth at each panel exon", "Reads per exon divided by exon length and total reads; one feature per exon.", "independent_paper", "ref 18 (Esfahani et al. 2022)"),
    "E1 Depth": ("e1-depth", "Normalised fragment read depth at first coding exons", "As all-exon depth, first coding exon of each gene only.", "independent_paper", "ref 18 (Esfahani et al. 2022)"),
    "Full Gene Depth": ("full-gene-depth", "Normalised fragment read depth per gene", "Depth with all exons of a gene combined into one feature.", "independent_paper", "ref 18 (Esfahani et al. 2022)"),
    "All Exons SE": ("all-exons-se", "Fragment-size Shannon entropy at each panel exon", "Shannon entropy of fragment-length frequencies per exon.", "author_reported", "refs 18 and 19 (the authors' 2023 panel study)"),
    "E1 SE": ("e1-se", "Fragment-size Shannon entropy at first coding exons", "Shannon entropy of fragment-length frequencies at first exons; the authors' 2023 panel metric.", "author_reported", "ref 19 (the authors' 2023 panel study)"),
    "All Exons MDS": ("all-exons-mds", "End-motif diversity score at each panel exon", "Normalised Shannon entropy of 256 4-mer end motifs per exon.", "independent_paper", "ref 23 (Jiang et al. 2020)"),
    "E1 MDS": ("e1-mds", "End-motif diversity score at first coding exons", "Motif diversity score at first exons only.", "independent_paper", "ref 23 (Jiang et al. 2020)"),
    "All Exons Small Fragments": ("all-exons-small-fragments", "Small-fragment proportion at each panel exon", "Proportion of fragments of 150 bp or less per exon.", "independent_paper", "ref 21"),
    "E1 Small Fragments": ("e1-small-fragments", "Small-fragment proportion at first coding exons", "Proportion of fragments of 150 bp or less at first exons.", "independent_paper", "ref 21"),
    "Fragment Bins": ("fragment-bins", "Fragment-length bin proportions at each panel exon", "Proportions of fragments in six length bins (0-100 to >300 bp) per exon.", "independent_paper", "refs 18 and 19"),
    "TFBS Entropy": ("tfbs-entropy", "Fragment-size entropy at transcription factor binding sites", "Shannon entropy of fragment lengths over the top 5,000 GTRD sites of each of 808 transcription factors.", "independent_paper", "refs 16 and 17 (Ulz et al. 2019; Doebley et al. 2022)"),
    "ATAC Entropy": ("atac-entropy", "Fragment-size entropy at cancer-specific open chromatin", "Shannon entropy of fragment lengths over TCGA ATAC-seq peaks of 23 cancer types.", "independent_paper", "ref 24 (Sun et al. 2019)"),
    "All Combined": ("all-combined", "All panel fragmentomic metrics combined", "All of the above metrics in one model.", "author_reported", "combination defined by the authors"),
    "Griffin": ("griffin", "Griffin", "Nucleosome profiling of cfDNA fragment coverage around transcription factor binding sites (central coverage, mean coverage, amplitude); here at the binding sites of 808 transcription factors. The method record names the published tool, not an implementation.", "independent_paper", "ref 17 (Doebley et al. 2022)"),
}
CFG = {}
for label, (key, name, desc, origin, cite) in METRICS.items():
    mid = f"{P}-method-{key}"
    B.method(mid, name, desc + f" Cited in the source as {cite}.", SRC, ["conventional_pipeline"],
             "Results P5; Methods P24-P30; Figure S3 legend", reported=label)
    CFG[label] = f"{P}-config-{key}"
    B.configuration(CFG[label], f"{name}, GLMnet multinomial classifier (Helzer et al. 2025)", mid, SRC, label,
                    "Tables S1-S2 row label; Methods P23-P30", ["supervised_machine_learning"],
                    "Re-implemented by the authors; no code release or version is printed",
                    f"{label} features from panel reads (20-500 bp inserts); elastic-net multinomial logistic regression (GLMnet), hyperparameters by Latin hypercube search with 5-fold inner cross-validation, up-sampling of minority classes")

# ---------------------------------------------------------------- protocols
LIM = ["Targeted exon-panel sequencing of metastatic cancers, not whole-genome sequencing of a screening population.",
       "AUROC values are medians over 25 replicates of 10-fold cross-validation; no interval is printed.",
       ("Methods P23 names GLMnet multinomial logistic regression for cancer-type and cancer-vs-healthy predictions; whether the "
        "'Normal' (healthy vs all cancers) AUROC comes from the multinomial model or a separate binary model is not stated."),  # review H2
       "The authors state that the study compares metrics rather than producing a locked prediction model.",
       "The article text cites the UW cohort results as Table S1 and the GRAIL results as Table S2, but the supplementary PDF captions label the GRAIL table S1 and the UW table S2. Locators here follow the PDF captions; the values quoted in the text match the tables as captioned in the PDF.",
       ("The Figure 4 and 5 legends call the plotted value the average AUROC of 25 repeats; the table captions and Methods P23 "
        "say median. Values here follow the tables.")]  # review H2
PR, DS = {}, {"grail": D_G, "uw": D_U}
for cohort, cname, cols, n in (("grail", "Razavi et al. 2019 GRAIL cohort", COLS_GRAIL, "151 cancers and 47 healthy donors"),
                               ("uw", "UW cohort", COLS_UW, "404 cancers and 27 healthy donors")):
    for panel in PANELS:
        pk = f"{cohort}-{PKEY[panel]}"
        PR[pk] = f"{P}-protocol-{pk}"
        genes = ("all genes of the cohort's panel" if panel == "Full panel" else f"only genes shared with the {panel} panel")
        B.rec(PR[pk], "protocol", f"Helzer et al. 2025 {cname}, {panel.lower() if panel == 'Full panel' else panel + ' gene subset'}: multinomial phenotype AUROC",
              f"Panel fragmentomic metrics computed on {genes}; one multinomial model per metric predicts {', '.join(cols)}.", SRC,
              [{"relation": "uses_data", "target_id": DS[cohort]}],
              {"protocol": (f"For each metric, a GLMnet multinomial model is trained and scored by 10-fold cross-validation with the same "
                            f"folds for every metric, repeated with 25 seeds; the reported AUROC per phenotype is the median over the "
                            f"25 replicates, and 'Mean AUROC' is the mean over phenotypes. Features use {genes}."),
               "version": f"Helzer et al. 2025, Supplementary Table {'S1' if cohort == 'grail' else 'S2'} (PDF caption), block '{panel if panel != 'Full panel' else ('GRAIL' if cohort == 'grail' else 'UW')}'",
               "metric": "auroc", "metric_direction": "higher", "limitations": LIM,
               "source_locator": f"Supplementary Table {'S1' if cohort == 'grail' else 'S2'}; Results P7-P12; Methods P23"})

# Review H1: Table S2 prints the UW commercial block as 'Foundation One CDx'; locators quote the printed label.
H1_OLD = "Supplementary Table S2 (PDF caption), block 'FoundationOne Liquid CDx'"
H1_NEW = ("Supplementary Table S2 (PDF caption), block 'Foundation One CDx' (printed label; the article names this subset "
          "FoundationOne Liquid CDx)")
H1_LIMIT = ("Supplementary Table S2 prints this block as 'Foundation One CDx'; the article text (Results P11-P12) names the subset "
            "FoundationOne Liquid CDx (309 genes; 77% of them available on the UW panel).")
REC = {r["id"]: r for r in B.records}
a = REC[PR["uw-foundationone"]]["attributes"]
a["version"] = a["version"].replace(H1_OLD, H1_NEW)
a["limitations"] = a["limitations"] + [H1_LIMIT]
REV = B.review(["pdf-text-parse"], PDF, PDF_URL,
               "Extracted by deterministic parse of the PDF text layer (pdftotext -layout) with headers, metric labels per panel block, "
               "panel labels and every row mean asserted; column order cross-checked against values quoted in the article text.")
J_COLS = {"grail": COLS_GRAIL + ["Mean AUROC"], "uw": COLS_UW + ["Mean AUROC"]}
n_res = 0
for cohort, blocks in BLOCKS.items():
    table = "S1" if cohort == "grail" else "S2"
    for k, blk in enumerate(blocks):
        panel = PANELS[k]
        pk = f"{cohort}-{PKEY[panel]}"
        for ln, label, _, vals in blk:
            key = METRICS[label][0]
            ev = f"{P}-eval-{pk}-{key}"
            lim = ["The same group published the first-exon entropy metric on targeted panels (2023)."] if METRICS[label][3] == "author_reported" else \
                  ["Re-implemented by the authors on panel exons from a whole-genome method published by another group."]
            B.evaluation(ev, f"{label} on {pk.replace('-', ' ')} (Helzer et al. 2025)", CFG[label], PR[pk], DS[cohort], SRC,
                         METRICS[label][3],
                         {"dataset_version": B.records[[r['id'] for r in B.records].index(DS[cohort])]["attributes"]["version"],
                          "split": "10-fold cross-validation, 25 seeds, same folds for all metrics",
                          "population": "151 cancers and 47 healthy donors" if cohort == "grail" else "404 cancers and 27 healthy donors",
                          "inputs": f"{label} features; {panel if panel != 'Full panel' else 'full cohort panel'} genes",
                          "adaptation": "GLMnet multinomial model trained within each training fold",
                          "metric_implementation": "One-vs-rest AUROC per phenotype from the multinomial model",
                          "aggregation": "Median over 25 replicates", "budget": None},
                         f"Supplementary Table {table}, block '{panel}', row '{label}' (text layer line {ln})", limitations=lim,
                         missing={"comparison.budget": {"reason": "inapplicable"}})
            for col, v in zip(J_COLS[cohort], vals):
                ck = "mean" if col == "Mean AUROC" else col.lower()
                if col == "Mean AUROC":
                    q = f"mean over {len(vals) - 1} phenotypes of the median one-vs-rest AUROCs; {panel} genes"
                elif col == "Normal":
                    q = f"healthy (Normal) vs all cancers, one-vs-rest, median of 25 replicates; {panel} genes"
                else:
                    q = f"{col} vs all other classes, one-vs-rest, median of 25 replicates; {panel} genes"
                B.result(f"{ev.replace('-eval-', '-result-')}-auroc-{ck}", ev, SRC,
                         f"Supplementary Table {table} (PDF caption), block '{panel}', row '{label}', column '{col}'".replace(H1_OLD, H1_NEW),
                         v, "auroc", q, "unitless", REV)
                n_res += 1
expect(n_res, 52 * 5 + 53 * 10, "result count")

CREV = B.review(["transcription"], XML, XML_URL, "Hand transcription from the article text, checked by string match in extract/extract_helzer2025.py.")
B.claim(f"{P}-claim-low-fraction-mixing", PR["grail-full"], "related_result",
        ("In silico mixing of GRAIL-cohort cancer and healthy reads (70% training, 30% validation; mixtures 50:50 to 1:99 at 100 M reads) "
         "showed all metrics losing AUROC as ctDNA fraction fell, with depth at all exons best; at 0.0001-0.001 ctDNA fraction many "
         "AUROCs approached 0.5. The values are shown only in Figure 6B and are not stored as results."),
        [S_ART], "Results P15-P17; Figure 6; Methods P31", CREV)

# ---------------------------------------------------------------- judgements
J = "use-case-mapping-ctdna-lit-20261011-helzer2025"
CONS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
        "Use the 'Normal' (healthy vs all cancers) results for detection; the other columns are cancer-type or subtype discrimination.",
        "Do not combine with whole-genome fragmentomics results from other protocols; panel, cohort and classifier differ."]
REASON = "Add the multi-metric panel fragmentomics comparison of Helzer et al. 2025 (Nature Communications), retrieved 2026-10-11."
H3_METRICS = {"grail": "12 fragmentomic metrics and their combination", "uw": "12 fragmentomic metrics, their combination and Griffin"}  # review H3
links = []
for order, (cohort, label) in enumerate((("grail", "Razavi et al. 2019 GRAIL cohort, full panel"), ("uw", "UW cohort, full panel")), start=1):
    pk = f"{cohort}-full"
    jid = f"{J}-{pk}"
    B.judgement(jid, UC_FRAG, Q_FRAG, PR[pk], "proxy",
                f"Healthy vs all-cancer one-vs-rest AUROC (and per-cancer-type AUROC) for {H3_METRICS[cohort]} on the same targeted-panel cfDNA samples, same folds: {label}",
                ("Compares many fragmentomic metric classes, adapted to exon panels by the authors, (length, depth, end motifs, TFBS and open-chromatin entropy, "
                 "Griffin in the UW cohort) on the same plasma samples with one classifier and shared folds. Proxy: inputs are "
                 "targeted exon panels rather than whole-genome sequencing, the cancers are metastatic, the endpoint is AUROC "
                 "without a fixed false-positive constraint, and the low-tumour-fraction analysis is figure-only."),
                CONS, LIM, [(S_ART, "Results P5-P8; Methods P23-P31"), (S_SI, f"Supplementary Table {'S1' if cohort == 'grail' else 'S2'}")],
                REASON, "helzer2025-panel-fragmentomics", "Fragmentomic metrics on targeted cfDNA panels (Helzer et al. 2025)",
                "auroc", label, order)
    links.append({"use_case": UC_FRAG, "relation": "assessed_by", "target_id": PR[pk], "judgement_claim": jid})

REVIEWED = {f"{J}-{c}-full": [r["id"] for r in B.records if r["kind"] == "evaluation" and r["attributes"]["protocol"] == PR[f"{c}-full"]]
            for c in ("grail", "uw")}
expect((len(REVIEWED[f"{J}-grail-full"]), len(REVIEWED[f"{J}-uw-full"])), (13, 14), "reviewed evaluations")
B.finalize("Re-downloaded the pinned artifacts and matched their SHA-256; compared all 790 cells with a separate parser of the "
           "pdftotext layout text written for this review (the extractor's script was not run), with panel blocks fixed by row "
           "order, every Mean AUROC checked against its row mean and the UW column order checked from the word bounding boxes of "
           "the rotated header; compared 44 values by eye against rendered pages 8 and 9 of the PDF.",
           ["source-hash-verification", "pdf-text-parse", "independent-cell-check", "rendered-source-visual-check"], REVIEWED)
B.write(BATCH, links)
