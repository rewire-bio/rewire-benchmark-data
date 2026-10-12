"""Deterministic extraction of the tumour-fraction-stratified results of Fragmentia-AI WGS (Molecular Biomedicine 2026).

Usage: python3 -I extract_fragmentiawgs2026.py <download-dir> <batch-dir>

Reads two pinned artifacts:
  - the article, PMC13469060 full-text JATS XML (10.1186/s43556-026-00538-w)
  - Supplementary Material 1 (43556_2026_538_MOESM1_ESM.docx), Table S4, read from the DOCX table XML
Extracts every cell of Table S4 (sensitivity of low-TF cancers by stage group and cohort at the predefined cutoff) and
every printed performance value in Results P13, P14, P19 and P21 (AUC overall and by ichorCNA tumour-fraction stratum
for the three fine-tuning schemes, sensitivity and specificity at the predefined cutoff, external DELFI cohort). Each
value is parsed from an asserted sentence. Writes batch.jsonl, claims.csv and use-case-links.json.

Depends on ctdnalit-20261011-fragmentia2026-method-fragmentia-ai (batch use-case-coverage-ctdna-fragmentia2026-20261011).

Corrections from the independent review (docs/reviews/use-cases/plasma-ctdna-use-cases-2026-10-12.md) are applied here
and marked with their review item (A2, W1 to W4); B.finalize applies the review to every record.
"""
import os, re, sys, zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (Batch, UC_FRAG, Q_FRAG, sha, expect)  # noqa: E402

DL, BATCH = sys.argv[1], sys.argv[2]
B = Batch("ctdnalit-20261011-fragmentiawgs2026", "2026-10-11")
P = B.P
XML, DOCX = f"{DL}/fragwgs/PMC13469060.xml", f"{DL}/fragwgs/43556_2026_538_MOESM1_ESM.docx"
XML_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13469060/fullTextXML"
DOCX_URL = "https://static-content.springer.com/esm/art%3A10.1186%2Fs43556-026-00538-w/MediaObjects/43556_2026_538_MOESM1_ESM.docx"
S_ART, S_SUP = f"{P}-source-article", f"{P}-source-supplementary-material-1"
SRC = [S_ART, S_SUP]
M_FA = "ctdnalit-20261011-fragmentia2026-method-fragmentia-ai"

root = ET.parse(XML).getroot()
PS = [" ".join("".join(p.itertext()).split()) for p in root.iter("p")]


def para(i, *frags):
    for f in frags:
        expect(f in PS[i], True, f"P{i} sentence: {f[:60]}")
    return PS[i]


para(8, "Model fitting used the training cohort (n = 3,695), and hyperparameter optimization and model selection used the internal validation cohort (n = 2,043; Table S1).",
     "The final model was evaluated in an independent test cohort (n = 5,996; Table S2) and externally validated in the public DELFI dataset (n = 538).",
     "TF strata were defined using ichorCNA-estimated tumor fraction as low (< 3%), medium (3–5%), or high (> 5%).")
p13 = para(13, "When the model was trained and fine-tuned on high-TF samples alone, it achieved an AUC of 0.982 in the training cohort, which consisted exclusively of high-TF samples",
           "In the validation cohort, performance remained high in high-TF samples (AUC: 0.988) but declined with decreasing TF (medium TF: 0.905; low TF: 0.652), yielding an overall AUC of 0.769",
           "Adding medium-TF samples preserved strong high-TF performance and modestly improved medium-TF discrimination, but low-TF performance remained limited (AUC: 0.702)")
p14 = para(14, "the model achieved AUCs of 0.924 (95% CI: 0.916–0.932) and 0.917 (95% CI: 0.905–0.929) in the training and validation cohorts, respectively",
           "At the prespecified cutoff corresponding to 98% specificity in training (score = 1.4650357), sensitivity was 0.58 and 0.61 in the two cohorts",
           "Low-TF AUC increased to 0.905 (95% CI: 0.894–0.916) in training and 0.884 (95% CI: 0.868–0.901) in validation")
p19 = para(19, "The model achieved an overall AUC of 0.930 (95% CI: 0.924–0.936)",
           "AUCs were 0.984 (95% CI: 0.979–0.989) for high-TF, 0.958 (95% CI: 0.940–0.976) for medium-TF, and 0.910 (95% CI: 0.902–0.917) for low-TF samples",
           "Using the predefined threshold, the model achieved an overall sensitivity of 0.58 and specificity of 0.97 in the test cohort",
           "Sensitivity increased with TF, from 0.46 in low-TF to 0.72 in medium-TF and 0.91 in high-TF samples")
p21 = para(21, "The DELFI cohort included 538 subjects, comprising 262 noncancer controls (48.7%) and 276 cancer patients across eight tumor types",
           "achieving an AUC of 0.929 (95% CI: 0.907–0.951)",
           "At the predefined cutoff threshold, the model achieved an overall sensitivity of 0.78 and specificity of 0.92")
para(37, "TF-stratified performance could not be evaluated in the DELFI cohort because BAM files required for ichorCNA were unavailable")
para(41, "This cohort included 3,044 noncancer controls and 2,952 cancer patients and was independent of the training and validation cohorts at the sample, patient, medical-center, and sequencing-batch levels.",
     "which comprised 262 noncancer controls and 276 cancer patients from the FinaleDB database")
para(45, "Training and validation cohorts were sequenced to approximately 0.1 × coverage, whereas the independent test, clinical evaluation, and analytical variability cohorts were sequenced to approximately 0.05 × coverage.")
para(60, "Low-Rank Adaptation (LoRA) [32] was applied to the query, key, and value (Wqkv) matrices of the DNABERT-2 backbone")
para(75, "are employees of Nanjing Geneseeq Technology Inc.")
FLAT = " ".join(PS)
expect("Together, they comprised 5,738 plasma samples, including 2,394 noncancer controls and 3,344 cancer patients across 17 cancer types." in FLAT, True, "train+validation composition")

# ---------------------------------------------------------------- Table S4 from the DOCX
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
doc = ET.fromstring(zipfile.ZipFile(DOCX).read("word/document.xml"))
body = list(doc.find(f"{W}body"))
tbls = [el for el in body if el.tag == f"{W}tbl" and "".join(el.itertext()).startswith("Table S4. Sensitivity of low-TF samples stratified by clinical stage group and cohort")]
expect(len(tbls), 1, "Table S4 (caption is the first row of the table)")
trs = [[" ".join("".join(tc.itertext()).split()) for tc in tr.findall(f"{W}tc")] for tr in tbls[0].findall(f"{W}tr")]
expect(trs[0], ["Table S4. Sensitivity of low-TF samples stratified by clinical stage group and cohort"], "Table S4 caption row")
expect(trs[1], ["Dataset", "Stage group", "No. of low-TF cancer samples", "No. of cancer samples detected as positive", "Sensitivity (95% CI)"], "Table S4 header")
rows = [r for r in trs[2:] if r and r[0] in ("Train", "Validation", "Test")]
expect([(r[0], r[1]) for r in rows], [("Train", "I/II"), ("Train", "III/IV"), ("Validation", "I/II"), ("Validation", "III/IV"), ("Test", "I/II"), ("Test", "III/IV")], "Table S4 rows")
S4 = re.compile(r"^(\d\.\d{3}) \((\d\.\d{3}) – (\d\.\d{3})\)$")
for r in rows:
    expect(bool(S4.match(r[4])), True, f"Table S4 {r[0]} {r[1]} sensitivity format")
    expect(round(int(r[3]) / int(r[2]), 3), float(S4.match(r[4]).group(1)), f"Table S4 {r[0]} {r[1]} sensitivity against counts")

# ---------------------------------------------------------------- sources
B.source(S_ART, "Generalizable cancer detection from ultra-low-pass WGS via deep contextual modeling of cfDNA sequences",
         "Primary source retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1186/s43556-026-00538-w", "artifact_url": XML_URL,
          "version": "Molecular Biomedicine, published online 2026-08-12; Europe PMC full-text JATS XML of PMC13469060",
          "retrieved_at": "2026-10-11T21:51:36Z", "artifact_sha256": sha(XML), "doi": "10.1186/s43556-026-00538-w",
          "publication_status": "peer_reviewed", "licence": "CC-BY-4.0", "media_type": "application/xml",
          "source_locator": ("Full artifact bytes; per-record locators on each record. 'Pn' is the zero-based index of the <p> "
                             "element in document order in this JATS XML, front matter included."),  # review A2
          "archive_sha256": sha(f"{BATCH}/artifacts/fragmentiawgs2026-article.xml.gz"),
          "archive_note": "gzip -n -9 copy of the exact bytes in artifacts/fragmentiawgs2026-article.xml.gz (CC BY 4.0)",
          "scope_note": ("Developer study: eleven authors are employees of Nanjing Geneseeq Technology Inc., which collected and sequenced "
                         "the cohorts and developed the model. Sequencing data and code are available only on request through a "
                         "Geneseeq data-use licence portal.")})
B.source(S_SUP, "Fragmentia-AI WGS paper, Supplementary Material 1 (Tables S1-S4, Figures S1-S9)",
         "Supplementary DOCX retrieved and hashed for the 2026-10-11 plasma ctDNA literature pass.",
         {"url": "https://doi.org/10.1186/s43556-026-00538-w", "artifact_url": DOCX_URL,
          "version": "43556_2026_538_MOESM1_ESM.docx, publisher supplementary file", "retrieved_at": "2026-10-11T21:52:25Z",
          "artifact_sha256": sha(DOCX), "doi": "10.1186/s43556-026-00538-w", "publication_status": "peer_reviewed",
          "licence": "CC-BY-4.0", "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
          "source_locator": "Table S4", "retrieval_note": "The same bytes are served inside the Europe PMC supplementaryFiles bundle for PMC13469060 (checked 2026-10-11T21:51:38Z).",
          "archive_note": "Not archived: the 2.5 MB DOCX is mostly figure images and is a stable publisher object pinned by hash."})

# ---------------------------------------------------------------- datasets
D = {k: f"{P}-data-{k}" for k in ("train", "validation", "test", "delfi-finaledb")}
GSC = "Retrospective Geneseeq repository samples, first baseline pretreatment sample per person; 17 cancer types; tumour fraction by ichorCNA."
B.rec(D["train"], "dataset", "Fragmentia-AI WGS training cohort (3,695 samples, 0.1x ULP-WGS)", "Training cohort, multi-centre, collected 2021-2023.", SRC,
      attributes={"version": "Fragmentia-AI WGS paper training cohort", "total": 3695, "positives": 2450, "negatives": 1245,  # review W1
                  "population": "Cancer and non-cancer samples (Table S1); low-TF cancers 66.1% of cancers Table S1: 2,450 cancers and 1,245 non-cancer controls.",
                  "assay": "ULP-WGS of plasma cfDNA, about 0.1x, DNBSEQ-T7", "scope_note": GSC, "source_locator": "Results P8-P9; Methods P40, P45; Table S1"})
B.rec(D["validation"], "dataset", "Fragmentia-AI WGS internal validation cohort (2,043 samples, 0.1x ULP-WGS)", "Validation cohort from the same centres, collected 2024-2025, used for model selection.", SRC,
      attributes={"version": "Fragmentia-AI WGS paper validation cohort", "total": 2043, "positives": 894, "negatives": 1149,  # review W1
                  "population": "Cancer and non-cancer samples (Table S1); low-TF cancers 62.3% of cancers Table S1: 894 cancers and 1,149 non-cancer controls.",
                  "assay": "ULP-WGS of plasma cfDNA, about 0.1x, DNBSEQ-T7", "scope_note": GSC + " Used for hyperparameter optimisation and model selection.",
                  "source_locator": "Results P8-P9; Methods P40, P45; Table S1"})
B.rec(D["test"], "dataset", "Fragmentia-AI WGS independent test cohort (5,996 samples, 0.05x ULP-WGS)", "Test cohort from different centres, independent at sample, patient, centre and batch level.", SRC,
      attributes={"version": "Fragmentia-AI WGS paper test cohort", "total": 5996, "positives": 2952, "negatives": 3044,
                  "population": "2,952 cancers (17 types; low-TF 71.6%) and 3,044 non-cancer controls (Table S2)",
                  "assay": "ULP-WGS of plasma cfDNA, about 0.05x, DNBSEQ-T7", "scope_note": GSC, "source_locator": "Results P8-P9; Methods P41, P45; Table S2"})
B.rec(D["delfi-finaledb"], "dataset", "DELFI cohort from FinaleDB as used by the Fragmentia-AI WGS paper (538 samples)", "Public DELFI (Cristiano et al. 2019) cfDNA WGS from FinaleDB: 276 cancers of eight types and 262 non-cancer controls.", SRC,
      attributes={"version": "FinaleDB DELFI data as used by the Fragmentia-AI WGS paper", "total": 538, "positives": 276, "negatives": 262,
                  "population": "276 cancers across eight tumour types and 262 non-cancer controls",
                  "assay": "WGS of plasma cfDNA, 100-bp paired-end, Illumina HiSeq 2000/2500",
                  "scope_note": ("Same study as the DELFI 2019 cohort behind existing fragmentomics judgements (amp-20261007 and the Hou et al. 2024 and "
                                 "Wang et al. 2026 batches), so the samples overlap. No ichorCNA tumour fraction was computed for it."),
                  "source_locator": "Results P21; Methods P41, P45"})

# ---------------------------------------------------------------- configurations
CFG = {k: f"{P}-config-{k}" for k in ("high-tf", "high-medium-tf", "high-medium-low-tf")}
NAMES = {"high-tf": "high-TF-only fine-tuning", "high-medium-tf": "high/medium-TF sequential fine-tuning", "high-medium-low-tf": "high/medium/low-TF sequential fine-tuning (final model)"}
for k, cid in CFG.items():
    B.configuration(cid, f"Fragmentia-AI WGS, {NAMES[k]}", M_FA, SRC, NAMES[k], "Results P8, P13-P14; Methods P47-P60", ["foundation_model"],
                    "Code and data on request through a Geneseeq data-use licence portal; no public weights",
                    f"DNABERT-2 backbone with LoRA on Wqkv, gated-attention MIL pooling and MLP; {NAMES[k]} on ichorCNA tumour-fraction strata of the training cohort",
                    fm=True, version_note="No release, commit or checkpoint name is printed")

# ---------------------------------------------------------------- protocols
LIM = ["Developer study: Geneseeq employees collected and sequenced the cohorts, developed the model and report every value.",
       ("Tumour-fraction strata are ichorCNA estimates, not measured fractions; the authors chose the 3% cutoff because the ichorCNA "
        "study reported 0.03 as its lower limit for detecting tumour from ULP-WGS (Results P8), so the low stratum holds cancers whose "
        "tumour fraction ichorCNA cannot resolve."),  # review W2
       "Retrospective case-control cohorts of clinically diagnosed cancers and non-cancer controls; not a screening population.",
       "The cutoff is set at 98% specificity in the training cohort and applied unchanged; observed specificity in other cohorts differs (0.97 in the test cohort, 0.92 in the DELFI cohort).",
       "No comparator method is evaluated on these cohorts; only Fragmentia-AI configurations are compared."]
PR = {k: f"{P}-protocol-{k}" for k in ("train", "validation", "test", "delfi")}
W4 = ("The training cohort has 1,245 non-cancer controls, the same number as the ULP-WGS cohort of the Fragmentia-AI paper (Cell "
      "Reports Medicine 2026) from the same company, so the two studies may share samples; neither paper says.")  # review W4
PROT = {
    "train": ("Training cohort (resubstitution)", "Performance on the 3,695-sample training cohort used to fit the model.", ["Training-set performance, not held out.", W4]),
    "validation": ("Internal validation cohort by ichorCNA tumour fraction", "AUC overall and within ichorCNA tumour-fraction strata on the 2,043-sample validation cohort used for model selection.", ["Used for hyperparameter optimisation and model selection, so not an independent test.", W4]),
    "test": ("Independent test cohort by ichorCNA tumour fraction", "AUC and sensitivity at the predefined cutoff, overall and within ichorCNA tumour-fraction strata, on the 5,996-sample independent test cohort.", ["Sequenced at about 0.05x against about 0.1x for training.", W4]),
    "delfi": ("External DELFI cohort (FinaleDB)", "AUC, sensitivity and specificity at the predefined cutoff on 538 public DELFI samples sequenced on another platform.", ["No tumour-fraction stratification; samples overlap the DELFI 2019 cohort used by other fragmentomics evidence."]),
}
for k, (title, desc, extra) in PROT.items():
    B.rec(PR[k], "protocol", f"Fragmentia-AI WGS paper: {title}", desc, SRC, [{"relation": "uses_data", "target_id": D['delfi-finaledb' if k == 'delfi' else k]}],
          {"protocol": desc + " Cancer vs non-cancer; ichorCNA TF strata low < 3%, medium 3-5%, high > 5%; cutoff score 1.4650357 (98% specificity in training).",
           "version": "Fragmentia-AI WGS paper (Molecular Biomedicine 2026), Results P13-P21; Supplementary Table S4",
           "metric": "auroc", "metric_direction": "higher", "limitations": LIM + extra,
           "source_locator": {"train": "Results P13-P14; Table S4", "validation": "Results P13-P14; Table S4", "test": "Results P19; Table S4", "delfi": "Results P21"}[k]})

REV_T = B.review(["transcription"], XML, XML_URL, "Values parsed by regular expression from Results sentences asserted verbatim in extract/extract_fragmentiawgs2026.py.")
REV_S4 = B.review(["deterministic-table-parse"], DOCX, DOCX_URL, "Extracted from the Table S4 XML of the DOCX with header, row labels and the sensitivity-count consistency asserted.")
EVS = {}


def ev(pk, ck, data):
    key = (pk, ck)
    if key not in EVS:
        EVS[key] = f"{P}-eval-{pk}-{ck}"
        B.evaluation(EVS[key], f"Fragmentia-AI WGS {NAMES[ck]} on the {PROT[pk][0].lower()}", CFG[ck], PR[pk], D[data], SRC, "author_reported",
                     {"dataset_version": B.records[[r['id'] for r in B.records].index(D[data])]["attributes"]["version"],
                      "split": {"train": "Training cohort", "validation": "Internal validation cohort (model selection)", "test": "Independent test cohort",
                                "delfi": "External public cohort"}[pk],
                      "population": "Cancer vs non-cancer", "inputs": "ULP-WGS cfDNA fragment sequences", "adaptation": NAMES[ck],
                      "metric_implementation": None, "aggregation": "Pooled over samples", "budget": None},
                     f"Results P{ {'train': '13-14', 'validation': '13-14', 'test': '19', 'delfi': '21'}[pk] }",
                     missing={"comparison.metric_implementation": {"reason": "unreported", "note": "AUC CI method not stated"}, "comparison.budget": {"reason": "inapplicable"}})
    return EVS[key]


def ci(lo, hi, txt):
    return {"type": "confidence_interval", "lower": lo, "upper": hi, "level": 0.95, "printed": txt, "note": "Method not stated"}


def res(pk, ck, data, rk, pv, metric, qual, loc, review=REV_T, unc=None, extra=None):
    e = ev(pk, ck, data)
    B.result(f"{e.replace('-eval-', '-result-')}-{rk}", e, SRC, loc, pv, metric, qual, "unitless" if metric == "auroc" else "fraction", review, uncertainty=unc, extra=extra)


CUT = "at the predefined cutoff (98% specificity in the training cohort)"
# P13: fine-tuning schemes
m = re.search(r"achieved an AUC of (0\.\d+) in the training cohort", p13); res("train", "high-tf", "train", "auroc-high-tf", m.group(1), "auroc", "high-TF cancers vs non-cancer (training cohort contains only high-TF cancers for this scheme)", "Results P13, sentence 1")
m = re.search(r"high-TF samples \(AUC: (0\.\d+)\) but declined with decreasing TF \(medium TF: (0\.\d+); low TF: (0\.\d+)\), yielding an overall AUC of (0\.\d+)", p13)
for rk, v, q in (("auroc-high-tf", m.group(1), "high-TF (> 5%) cancers vs non-cancer"), ("auroc-medium-tf", m.group(2), "medium-TF (3-5%) cancers vs non-cancer"),
                 ("auroc-low-tf", m.group(3), "low-TF (< 3%) cancers vs non-cancer"), ("auroc-overall", m.group(4), "all cancers vs non-cancer")):
    res("validation", "high-tf", "validation", rk, v, "auroc", q, "Results P13, sentence 2")
m = re.search(r"low-TF performance remained limited \(AUC: (0\.\d+)\)", p13)
res("validation", "high-medium-tf", "validation", "auroc-low-tf", m.group(1), "auroc", "low-TF (< 3%) cancers vs non-cancer", "Results P13, sentence 4")
# P14: final model
m = re.search(r"AUCs of (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\) and (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\) in the training and validation cohorts", p14)
res("train", "high-medium-low-tf", "train", "auroc-overall", m.group(1), "auroc", "all cancers vs non-cancer", "Results P14, sentence 1", unc=ci(m.group(2), m.group(3), f"95% CI: {m.group(2)}–{m.group(3)}"))
res("validation", "high-medium-low-tf", "validation", "auroc-overall", m.group(4), "auroc", "all cancers vs non-cancer", "Results P14, sentence 1", unc=ci(m.group(5), m.group(6), f"95% CI: {m.group(5)}–{m.group(6)}"))
m = re.search(r"sensitivity was (0\.\d+) and (0\.\d+) in the two cohorts", p14)
res("train", "high-medium-low-tf", "train", "sensitivity-cutoff", m.group(1), "recall", f"sensitivity, all cancers, {CUT}", "Results P14, sentence 3")
res("validation", "high-medium-low-tf", "validation", "sensitivity-cutoff", m.group(2), "recall", f"sensitivity, all cancers, {CUT}", "Results P14, sentence 3")
m = re.search(r"Low-TF AUC increased to (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\) in training and (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\) in validation", p14)
res("train", "high-medium-low-tf", "train", "auroc-low-tf", m.group(1), "auroc", "low-TF (< 3%) cancers vs non-cancer", "Results P14, sentence 5", unc=ci(m.group(2), m.group(3), f"95% CI: {m.group(2)}–{m.group(3)}"))
res("validation", "high-medium-low-tf", "validation", "auroc-low-tf", m.group(4), "auroc", "low-TF (< 3%) cancers vs non-cancer", "Results P14, sentence 5", unc=ci(m.group(5), m.group(6), f"95% CI: {m.group(5)}–{m.group(6)}"))
# P19: test cohort
m = re.search(r"overall AUC of (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\)", p19)
res("test", "high-medium-low-tf", "test", "auroc-overall", m.group(1), "auroc", "all cancers vs non-cancer", "Results P19, sentence 2", unc=ci(m.group(2), m.group(3), f"95% CI: {m.group(2)}–{m.group(3)}"))
m = re.search(r"AUCs were (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\) for high-TF, (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\) for medium-TF, and (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\) for low-TF", p19)
for j, (rk, q) in enumerate((("auroc-high-tf", "high-TF (> 5%) cancers vs non-cancer"), ("auroc-medium-tf", "medium-TF (3-5%) cancers vs non-cancer"), ("auroc-low-tf", "low-TF (< 3%) cancers vs non-cancer"))):
    v, lo, hi = m.group(3 * j + 1), m.group(3 * j + 2), m.group(3 * j + 3)
    res("test", "high-medium-low-tf", "test", rk, v, "auroc", q, "Results P19, sentence 3", unc=ci(lo, hi, f"95% CI: {lo}–{hi}"))
m = re.search(r"overall sensitivity of (0\.\d+) and specificity of (0\.\d+) in the test cohort", p19)
res("test", "high-medium-low-tf", "test", "sensitivity-cutoff", m.group(1), "recall", f"sensitivity, all cancers, {CUT}", "Results P19, sentence 5")
res("test", "high-medium-low-tf", "test", "specificity-cutoff", m.group(2), "specificity", f"non-cancer controls, {CUT}", "Results P19, sentence 5")
m = re.search(r"from (0\.\d+) in low-TF to (0\.\d+) in medium-TF and (0\.\d+) in high-TF samples", p19)
for rk, v, q in (("sensitivity-cutoff-low-tf", m.group(1), "low-TF (< 3%)"), ("sensitivity-cutoff-medium-tf", m.group(2), "medium-TF (3-5%)"), ("sensitivity-cutoff-high-tf", m.group(3), "high-TF (> 5%)")):
    res("test", "high-medium-low-tf", "test", rk, v, "recall", f"sensitivity, {q} cancers, {CUT}", "Results P19, sentence 6")
# P21: DELFI
m = re.search(r"achieving an AUC of (0\.\d+) \(95% CI: (0\.\d+)–(0\.\d+)\)", p21)
res("delfi", "high-medium-low-tf", "delfi-finaledb", "auroc-overall", m.group(1), "auroc", "all cancers vs non-cancer", "Results P21, sentence 3", unc=ci(m.group(2), m.group(3), f"95% CI: {m.group(2)}–{m.group(3)}"))
m = re.search(r"overall sensitivity of (0\.\d+) and specificity of (0\.\d+)", p21)
res("delfi", "high-medium-low-tf", "delfi-finaledb", "sensitivity-cutoff", m.group(1), "recall", f"sensitivity, all cancers, {CUT}", "Results P21, sentence 5")
res("delfi", "high-medium-low-tf", "delfi-finaledb", "specificity-cutoff", m.group(2), "specificity", f"non-cancer controls, {CUT}", "Results P21, sentence 5")
# Table S4
PK = {"Train": ("train", "train"), "Validation": ("validation", "validation"), "Test": ("test", "test")}
for r in rows:
    pk, data = PK[r[0]]
    s = S4.match(r[4])
    stage = "stage-i-ii" if r[1] == "I/II" else "stage-iii-iv"
    res(pk, "high-medium-low-tf", data, f"sensitivity-cutoff-low-tf-{stage}", s.group(1), "recall", f"sensitivity, low-TF (< 3%) stage {r[1]} cancers, {CUT}",
        f"Supplementary Table S4, row '{r[0]}' / '{r[1]}', column 'Sensitivity (95% CI)'", review=REV_S4,
        unc=ci(s.group(2), s.group(3), f"({s.group(2)} – {s.group(3)})"), extra={"numerator": int(r[3]), "denominator": int(r[2])})

# ---------------------------------------------------------------- judgements
J = "use-case-mapping-ctdna-lit-20261011-fragmentiawgs2026"
CONS = ["Inspect every linked evaluation's source locator and preserved limitations before citing a result.",
        "Tumour-fraction strata are ichorCNA estimates; do not read them as measured ctDNA fractions.",
        "Do not combine with other protocols' results; cohorts, depth and thresholds differ."]
REASON = "Add the tumour-fraction-stratified results of Fragmentia-AI WGS (Molecular Biomedicine 2026), retrieved 2026-10-11."
links = []
for order, (pk, label, endpoint, rationale) in enumerate((
        ("validation", "Internal validation cohort (model selection)",
         "AUC overall and within ichorCNA tumour-fraction strata for three fine-tuning schemes of one fragment-level model, plus sensitivity at the training-derived 98%-specificity cutoff",
         "Shows how a fragmentomic model's discrimination changes in low ichorCNA tumour fraction and how training on low-TF samples changes it. Proxy: one developer model, AUC rather than fixed-specificity sensitivity within strata (except Table S4), and the cohort was used for model selection."),
        ("test", "Independent test cohort",
         "AUC overall and within ichorCNA tumour-fraction strata, and sensitivity overall, by stratum and for low-TF cancers by stage at the training-derived 98%-specificity cutoff (observed specificity 0.97), on 5,996 independent samples",
         ("Measures the use case's endpoint for one workflow: detection within ichorCNA tumour-fraction strata, including below 3%, "
          "at a cutoff fixed in advance at 98% specificity in the training cohort and applied unchanged to an independent test cohort "
          "of 2,952 cancers and 3,044 non-cancer controls that was not used for fitting or model selection (observed specificity 0.97). "
          "Direct despite its limitations: the strata are ichorCNA estimates rather than measured tumour fractions, no comparator "
          "method is run on the cohort, the cohort is retrospective case-control, and the developer reports every value.")),  # review W3
        ("delfi", "External DELFI cohort",
         "AUC, sensitivity and specificity at the predefined cutoff on 538 public DELFI samples from another sequencing platform",
         "An external-platform check of a fragmentomic model on the public DELFI cohort. Proxy: no tumour-fraction strata, specificity falls to 0.92 at the transferred cutoff, and the samples overlap the DELFI 2019 cohort behind other evidence for this use case.")), start=1):
    jid = f"{J}-{pk}"
    relevance = "direct" if pk == "test" else "proxy"  # review W3
    B.judgement(jid, UC_FRAG, Q_FRAG, PR[pk], relevance, endpoint, rationale, CONS, LIM + PROT[pk][2],
                [(S_ART, "Results P8-P21; Methods P40-P60"), (S_SUP, "Table S4")], REASON,
                "fragmentiawgs2026-tf-strata", "Fragmentia-AI WGS by ichorCNA tumour fraction (Molecular Biomedicine 2026)", "auroc", label, order)
    links.append({"use_case": UC_FRAG, "relation": "assessed_by", "target_id": PR[pk], "judgement_claim": jid})
REVIEWED = {f"{J}-test": [f"{P}-eval-test-high-medium-low-tf"],
            f"{J}-validation": [f"{P}-eval-validation-{k}" for k in ("high-tf", "high-medium-tf", "high-medium-low-tf")],
            f"{J}-delfi": [f"{P}-eval-delfi-high-medium-low-tf"]}
for jid, evs in REVIEWED.items():
    expect(sorted(evs), sorted(EVS[k] for k in EVS if f"{J}-{k[0]}" == jid), f"{jid} reviewed evaluations")
B.finalize("Re-downloaded the pinned artifacts and matched their SHA-256; read Table S4 from the DOCX table XML with a separate "
           "reader written for this review (the extractor's script was not run) and checked each sensitivity against "
           "detected/total; compared the text values with Results P13, P14, P19 and P21.",
           None, REVIEWED)
B.write(BATCH, links)
