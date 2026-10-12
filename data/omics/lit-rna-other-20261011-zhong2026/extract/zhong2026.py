"""Zhong et al. 2026 (arXiv 2602.22822v4, FlexMS): Table 2 from the text layer of the pinned PDF
(pdftotext 26.08.0 -layout).

Usage: python3 -I zhong2026.py <2602.22822v4.pdf> <pdftotext -layout output> <batch folder>
"""
import hashlib, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, finalise, review

pdf, txt_path, folder = sys.argv[1:4]
SHA = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
assert SHA == "44c83ca8a52abb2f625840cd7885fcdc1013419a1faaa5de6a7e8ccc672e546d", SHA
URL = "https://arxiv.org/pdf/2602.22822v4"
L = open(txt_path).read().split("\n")
i = next(k for k, l in enumerate(L) if l.strip().startswith("Table 2: Performance of different embedder-predictor combinations on the MassSpecGym dataset."))
EMB = ["CNN", "GCN", "GIN", "GAT", "Trans", "ESPF", "DL", "Attn", "AllDes", "CBTa", "GFv2"]
h = next(k for k in range(i, i + 8) if L[k].split()[:1] == ["Pred"])
assert L[h].split() == ["Pred"] + EMB, L[h]
num = r"(\d\.\d{3})"
sections, rows, sec = [], [], None
for l in L[h + 1:h + 9]:
    s = l.strip()
    if s in ("Cosine Similarity (Cos Sim)", "Jensen-Shannon Similarity (JS Sim)"):
        sec = s
        continue
    m = re.match(r"^(Mass|NEIMS|MolMS)\s+" + r"\s+".join([num] * 11) + r"\s*$", s)
    assert m, l
    rows.append((sec, m.group(1), m.groups()[1:]))
assert [(r[0], r[1]) for r in rows] == [(s, p) for s in ("Cosine Similarity (Cos Sim)", "Jensen-Shannon Similarity (JS Sim)") for p in ("Mass", "NEIMS", "MolMS")]

b = Batch(folder, "lit20261011-zhong2026", ["metabolomics"])
src = b.source("arxiv-2602-22822v4", "FlexMS: A Unified Public Benchmark for Molecule Tandem Mass Spectrum Prediction", {
    "url": "https://arxiv.org/abs/2602.22822v4", "artifact_url": URL, "version": "arXiv 2602.22822v4 (v1 submitted 2026-02-26; v4 dated 2026-06-24 on the PDF)",
    "retrieved_at": "2026-10-11T00:44:14Z", "artifact_sha256": SHA, "doi": "10.48550/arXiv.2602.22822",
    "publication_status": "preprint", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf"},
    "Primary source retrieved and hashed for the 2026-10-11 other-omics literature pass. Not archived (10.9 MB PDF).")

EMBNAME = {"CNN": "CNN", "GCN": "GCN", "GIN": "GIN", "GAT": "GAT", "Trans": "Transformer", "ESPF": "ESPF", "DL": "Daylight fingerprint",
           "Attn": "AttentiveFP", "AllDes": "All-Descriptors MLP", "CBTa": "ChemBERTa", "GFv2": "GraphormerV2"}
PRED = {"Mass": ("MassFormer", "Graph transformer spectrum predictor, used as the predictor head in FlexMS (Table 2 caption: 'Mass' denotes MassFormers)."),
        "NEIMS": ("NEIMS", "Neural electron-ionization mass spectrum predictor, used as a predictor head in FlexMS."),
        "MolMS": ("MolMS", "Point-cloud molecular spectrum predictor, used as a predictor head in FlexMS.")}
fam = {p: b.system("model", p, n, d, src, ["supervised_machine_learning"], {}) for p, (n, d) in PRED.items()}
data = b.dataset("massspecgym", "MassSpecGym (FlexMS spectrum prediction)", "MassSpecGym MS/MS spectra used for spectrum prediction in FlexMS.", src,
                 {"version": "MassSpecGym as loaded by FlexMS", "split": "MassSpecGym official split (Section 4.1 and Appendix C.1)",
                  "source_locator": "Section 4.1; Appendix C",
                  "missing_metadata": {"scored_count": {"reason": "unreported"}}})
prot = b.protocol("t2-massspecgym", "FlexMS molecule-to-spectrum prediction on MassSpecGym, embedder-predictor grid (Table 2)",
                  "Predict a binned MS/MS spectrum from a molecule with each embedder-predictor combination; score cosine and Jensen-Shannon similarity to the observed spectrum.",
                  src, data, {"protocol": "Embedder and predictor trained end to end with a cosine loss, AdamW, up to 100 epochs with early stopping on validation cosine, batch 512, seed 42 (Appendix C).",
                              "version": "Table 2", "task": "Molecule-to-MS/MS spectrum prediction", "source_locator": "Table 2 caption; Section 4.2; Appendix C",
                              "limitations": ["The Table 2 caption does not state the bin resolution; Section 4.2 refers to several resolutions.",
                                              "Single seed (42); no uncertainty reported.",
                                              "Bold, double-line and underline rank marks are not recorded."],
                              "missing_metadata": {"metric_implementation": {"reason": "unreported", "note": "Bin width for Table 2 not stated in the caption"}}})
# Review Z1: FlexMS uses its own binning and metrics, so the protocol evaluates the MassSpecGym task but is not part_of the benchmark.
next(r for r in b.records if r["id"] == prot)["links"].append({"relation": "evaluates_task", "target_id": "discovery-benchmark-massspecgym-spectrum-simulation"})
def rev(): return review(["pdf-text-parse"], SHA, URL, "Extracted from the pinned PDF text layer (pdftotext 26.08.0 -layout) by extract/zhong2026.py with the header row, section labels and predictor labels asserted.")
cfg, ev = {}, {}
for sec, pred, vals in rows:
    for e, v in zip(EMB, vals):
        if (pred, e) not in cfg:
            cfg[(pred, e)] = b.configuration(f"{pred}-{e}", f"{PRED[pred][0]} predictor with {EMBNAME[e]} embedder (FlexMS)", fam[pred], src,
                ["foundation_model"] if e in ("CBTa", "GFv2") else ["supervised_machine_learning"],
                {"version": "Trained by the benchmark authors in FlexMS", "configuration": {"embedder": EMBNAME[e], "predictor": PRED[pred][0]},
                 "source_locator": f"Table 2 row '{pred}', column '{e}'; caption abbreviations",
                 "missing_metadata": {"checkpoint": {"reason": "unreported"}}}, e in ("CBTa", "GFv2"))
            ev[(pred, e)] = b.evaluation(f"t2-{pred}-{e}", f"{PRED[pred][0]} with {EMBNAME[e]} on MassSpecGym spectrum prediction", cfg[(pred, e)], prot, data, src,
                "independent_paper", {"dataset_version": "MassSpecGym as loaded by FlexMS", "split": "MassSpecGym official split", "population": None,
                 "inputs": "Molecular structure", "adaptation": "Trained from scratch or fine-tuned end to end", "metric_implementation": None,
                 "aggregation": "Mean over test spectra", "budget": None}, f"Table 2 row '{pred}', column '{e}'",
                missing={"aggregation": {"reason": "unreported", "note": "Aggregation over test spectra is not stated in the caption"}})
        m = "spectrum-cosine-similarity" if sec.startswith("Cosine") else "jensen-shannon-similarity"
        b.result(f"t2-{pred}-{e}-{m}", ev[(pred, e)], src, m, "higher", "unitless", v,
                 f"Table 2 section '{sec}', row '{pred}', column '{e}'", rev(), qualifier="test split; bin resolution not stated in the caption",
                 name=f"{PRED[pred][0]} + {EMBNAME[e]} {m}")
finalise(b.records, "reviewer-ro-2",
         "Re-downloaded the arXiv PDF and matched its SHA-256. An independent regex parse of pdftotext -layout compared all 66 Table 2 cells (value, metric and predictor) with no mismatch; a seeded sample of 40 cells was read against the rendered PDF page and all matched.",
         methods=lambda r: ["source-hash-verification", "pdf-text-parse", "independent-cell-check"], extractor="lit-rna-other")
print(b.write())
