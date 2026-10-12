"""Khoo 2026 (arXiv 2610.02249v1, nearest-neighbour baselines for fingerprint prediction): Tables 1 and 2
from the text layer of the pinned PDF (pdftotext 26.08.0 -layout).

Usage: python3 -I khoo2026.py <2610.02249v1.pdf> <pdftotext -layout output> <batch folder>
"""
import hashlib, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, finalise, review

pdf, txt_path, folder = sys.argv[1:4]
SHA = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
assert SHA == "19c0dddb0e789f0dce3cdae73604206a0eab09f7ce411881108db6b937374f1e", SHA
URL = "https://arxiv.org/pdf/2610.02249v1"
L = open(txt_path).read().split("\n")
SIMS = ["Cosine", "Modified cosine", "Neutral-loss cosine", "Cosine Similarity (DreaMS)", "Binned cosine"]
EXPECT = [(1, s) for s in SIMS] + [(2, s) for s in SIMS] + [(3, s + " + sub-formula") for s in SIMS] + [(3, "Sub-formula rule only")]
COLS = [("NPLIB1", "Scaffold"), ("NPLIB1", "Random"), ("MassSpecGym", "Scaffold"), ("MassSpecGym", "Random")]
num = r"(\d\.\d{3})"

def table(caption_prefix):
    end = next(k for k, l in enumerate(L) if l.strip().startswith(caption_prefix))
    hdr = next(k for k in range(end - 1, end - 30, -1) if L[k].split()[:2] == ["Assumption", "Similarity"])
    assert L[hdr].split() == ["Assumption", "Similarity", "Scaffold", "Random", "Scaffold", "Random"], L[hdr]
    assert L[hdr - 1].split() == ["NPLIB1", "MassSpecGym"], L[hdr - 1]
    rows = []
    for l in L[hdr + 1:end]:
        m = re.search(r"(\S.*?)\s+" + r"\s+".join([num] * 4) + r"\s*$", l)
        if not m:
            continue
        lab = re.sub(r"\s+" + r"\s+".join([num] * 4) + r"\s*$", "", l).strip()
        lab = re.sub(r"^(\(\d\) (No chemical|Chemical|Formula-)|annotated peaks)\s{2,}", "", lab).strip()
        rows.append((lab, m.groups()[1:]))
    assert [r[0] for r in rows] == [e[1] for e in EXPECT], [r[0] for r in rows]
    return rows

t1 = table("Table 1: Binary Jaccard index (Tanimoto similarity) between the predicted and the true fingerprint")
t2 = table("Table 2: Cosine similarity between the raw prediction")

b = Batch(folder, "lit20261011-khoo2026", ["metabolomics"])
src = b.source("arxiv-2610-02249v1", "Nearest-neighbour baselines for fingerprint prediction from MS/MS spectra under different assumptions", {
    "url": "https://arxiv.org/abs/2610.02249v1", "artifact_url": URL, "version": "arXiv 2610.02249v1, submitted 2026-09-30",
    "retrieved_at": "2026-10-11T00:44:10Z", "artifact_sha256": SHA, "doi": "10.48550/arXiv.2610.02249",
    "publication_status": "preprint", "licence": "CC-BY-4.0", "media_type": "application/pdf"},
    "Primary source retrieved and hashed for the 2026-10-11 other-omics literature pass.")
nn = b.system("method", "nearest-neighbour-fingerprint", "Nearest-neighbour fingerprint retrieval",
              "Returns the fingerprint of the most similar training spectrum (or a weighted top-k consensus for the sub-formula rule) as the predicted fingerprint.",
              src, ["conventional_pipeline"], {})
ASSUME = {1: "No chemical formula: spectrum and precursor m/z only; retrieval over the whole training set.",
          2: "Chemical formula known: retrieval restricted to training spectra with the same formula, falling back to the whole set.",
          3: "Peaks annotated with sub-formulas of the ground-truth formula; same-formula retrieval with a sub-formula rule fallback, or the sub-formula rule alone."}
cfg = {}
for a, lab in EXPECT:
    params = ASSUME[a] + (" Sub-formula rule hyperparameters selected on the validation split (Note S5)." if a == 3 else "")
    if "DreaMS" in lab:  # review K1
        params += "; DreaMS pre-trained checkpoint without contrastive fine-tuning (Supplementary Note S2)"
        checkpoint = {"reason": "unreported", "note": "Pre-trained DreaMS checkpoint without contrastive fine-tuning (Note S2); the exact checkpoint file is not stated"}
    else:
        checkpoint = {"reason": "inapplicable", "note": "Retrieval method; no learned checkpoint"}
    cfg[(a, lab)] = b.configuration(f"a{a}-{lab}", f"Nearest neighbour, assumption ({a}), {lab}", nn, src,
        ["foundation_model"] if "DreaMS" in lab else ["conventional_pipeline"],
        {"version": "Author implementation (arXiv 2610.02249v1)", "parameters": params,
         "source_locator": "Section 1; Supplementary Notes S2 to S5", "missing_metadata": {"checkpoint": checkpoint}},
        "DreaMS" in lab)
SPLITN = {("NPLIB1", "Scaffold"): "12,909 / 2,688 / 2,689", ("NPLIB1", "Random"): "12,800 / 2,742 / 2,744",
          ("MassSpecGym", "Scaffold"): "76,243 / 16,041 / 16,042", ("MassSpecGym", "Random"): "75,828 / 16,248 / 16,250"}
LEAK = {"NPLIB1": "62.9%", "MassSpecGym": "95.3%"}  # review K2: Supplementary Table 3 structure leakage
data, prot = {}, {}
for ds, sp in COLS:
    data[(ds, sp)] = b.dataset(f"{ds}-{sp}", f"{ds}, {sp.lower()} split (Khoo 2026)", f"{ds} spectra under a {sp.lower()} split; train/validation/test {SPLITN[(ds, sp)]} (Table 3).", src,
        {"version": "As split in arXiv 2610.02249v1", "split": f"{sp} split, train/val/test {SPLITN[(ds, sp)]}", "source_locator": "Supplementary Note S1, Table 3"})
    for a in (1, 2, 3):
        prot[(ds, sp, a)] = b.protocol(f"{ds}-{sp}-a{a}", f"Fingerprint prediction from MS/MS, {ds} {sp.lower()} split, assumption ({a}) (Khoo 2026)",
            "Predict the Morgan fingerprint (radius 2, 4096 bits) of each test compound by nearest-neighbour retrieval against the training split.", src, data[(ds, sp)],
            {"protocol": ASSUME[a] + " Jaccard index on the prediction binarised at 0.5 and cosine on the raw prediction, averaged over the full test split.",
             "allowed_information": ASSUME[a], "version": "Tables 1 and 2", "task": "Molecular fingerprint prediction from MS/MS spectra",
             "source_locator": "Section 1; Supplementary Note S1", "limitations": ["Single author's baselines; no comparison with deep models in these tables.", "Bold best-per-column marks are not recorded."]
                            + ([f"Random split: {LEAK[ds]} of test spectra have their structure (first InChIKey block) in the training split (Supplementary Table 3); scores largely reflect retrieval of seen structures."] if sp == "Random" else [])})
def rev(): return review(["pdf-text-parse"], SHA, URL, "Extracted from the pinned PDF text layer (pdftotext 26.08.0 -layout) by extract/khoo2026.py with header rows and the 16 row labels asserted.")
ev = {}
for tn, rows, metric, q in (("1", t1, "fingerprint-tanimoto-similarity", "Morgan radius 2, 4096 bits; prediction binarised at 0.5; mean over the full test split"),
                            ("2", t2, "fingerprint-cosine-similarity", "Morgan radius 2, 4096 bits; raw prediction before thresholding; mean over the full test split")):
    for (a, lab), (printed_lab, vals) in zip(EXPECT, rows):
        for (ds, sp), v in zip(COLS, vals):
            k = (a, lab, ds, sp)
            if k not in ev:
                ev[k] = b.evaluation(f"{ds}-{sp}-a{a}-{lab}", f"Nearest neighbour ({lab}), assumption ({a}), {ds} {sp.lower()}", cfg[(a, lab)], prot[(ds, sp, a)], data[(ds, sp)], src,
                    "author_reported", {"dataset_version": "As split in arXiv 2610.02249v1", "split": f"{sp} split test", "population": "Full test split",
                     "inputs": ASSUME[a], "adaptation": "None (retrieval)", "metric_implementation": "Supplementary Note S1 formulas",
                     "aggregation": "Mean over test spectra", "budget": None}, f"Tables 1 and 2 row '{lab}' under assumption ({a}), column '{ds} {sp}'")
            b.result(f"t{tn}-{ds}-{sp}-a{a}-{lab}", ev[k], src, metric, "higher", "unitless", v,
                     f"Table {tn} assumption ({a}) row '{lab}', column '{ds}' / '{sp}'", rev(), qualifier=q, name=f"NN {lab} ({a}) {ds} {sp} {metric}")
finalise(b.records, "reviewer-ro-2",
         "Re-downloaded the arXiv PDF and matched its SHA-256 and the archived gzip. An independent regex parse of pdftotext -layout found the 32 data rows and compared all 128 cells (value, metric, assumption, dataset and split links, configuration) with no mismatch; a seeded sample of 40 cells was read against the rendered PDF pages and all matched.",
         methods=lambda r: ["source-hash-verification", "pdf-text-parse", "independent-cell-check"], extractor="lit-rna-other")
print(b.write())
