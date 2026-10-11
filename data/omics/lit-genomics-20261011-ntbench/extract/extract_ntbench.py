"""Nucleotide Transformer benchmark (Dalla-Torre et al., Nature Methods 2025): Supplementary Tables 6, 7 and 9.

Usage: python3 -I extract_ntbench.py <MOESM1.pdf> <pdftotext -layout output> <batch-folder>
"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import Batch, extraction_review, sha256

pdf, txt, folder = sys.argv[1:4]
SHA = sha256(pdf)
assert SHA == "ef0f357a1289aad1910059d455579e242a9a82ab3e32ec38d8ea2584effc436e", SHA
URL = "https://static-content.springer.com/esm/art%3A10.1038%2Fs41592-024-02523-z/MediaObjects/41592_2024_2523_MOESM1_ESM.pdf"
lines = open(txt).read().split("\n")

b = Batch(folder, "lit-genomics-20261011-ntbench")
SRC = b.source("lit-genomics-20261011-ntbench-source-dallatorre2025-si", "Nucleotide Transformer: Supplementary Information (Supplementary Tables 1-12)", {
    "url": "https://doi.org/10.1038/s41592-024-02523-z", "artifact_url": URL,
    "version": "Nature Methods 22, 287-297 (published online 2024-11-28); Supplementary Information PDF (MOESM1, 25 pages)",
    "retrieved_at": "2026-10-11T01:37:37Z", "artifact_sha256": SHA, "doi": "10.1038/s41592-024-02523-z",
    "publication_status": "peer_reviewed", "licence": "CC-BY-NC-ND-4.0", "media_type": "application/pdf",
    "limitations": ["Developer paper: the authors are InstaDeep and NVIDIA employees and developed the Nucleotide Transformer models (Competing interests). NT rows are author_reported.",
                    "Main-text Figure 2 and Extended Data are not read; the supplementary tables print the same per-task medians with standard deviations.",
                    "Supplementary Table 9 lists a DNABERT-1 fine-tuning average that has no per-task row in Supplementary Table 7."]})
SIDS = [SRC]
REV = lambda loc: extraction_review(["pdf-text-parse"], "Parsed the pdftotext -layout text of the pinned Supplementary Information PDF with tools/extract_ntbench.py: each block's 'Dataset' header gives six task columns, model rows matched as label followed by six 'value (± sd)' cells; block, row and column counts asserted. " + loc, SHA, URL)

TASKS = ["H2AFZ", "H3K27ac", "H3K27me3", "H3K36me3", "H3K4me1", "H3K4me2", "H3K4me3", "H3K9ac", "H3K9me3", "H4K20me1", "Enhancer", "Enhancer types",
         "Promoter all", "Promoter non-TATA", "Promoter TATA", "Splice acceptor", "Splice site all", "Splice donor"]
META = {}  # from Supplementary Table 5: train, test, max length
for l in lines:
    m = re.match(r"^(\S.*?)\s{2,}(\d+)\s+(\d+)\s+(\d+)\s+MCC\s+Human\s*$", l)
    if m:
        META[m.group(1).strip()] = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
assert sorted(META) == sorted(TASKS), META

BENCH = b.entity("benchmark", b.rid("benchmark", "nucleotide-transformer-benchmark"), "Nucleotide Transformer benchmark (18 tasks)",
    "Eighteen human genomic classification tasks (ten histone marks, enhancers, enhancer types, three promoter sets and three splice-site sets) scored by MCC with tenfold cross-validation.",
    SIDS, {"entity_level": "suite", "version": "Nature Methods 2025 (Supplementary Table 5)", "task": "Genomic sequence classification",
           "scope_note": "Probing (Supplementary Table 6) and parameter-efficient fine-tuning (Supplementary Table 7) of NT models, with DNABERT-2, HyenaDNA, Enformer, BPNet and randomly initialised controls.",
           "source_locator": "Supplementary Table 5; Supplementary Tables 6, 7 and 9"})
datas, protos = {}, {}
for t in TASKS:
    tr, te, ln = META[t]
    datas[t] = b.entity("dataset", b.rid("data", t), f"NT benchmark {t}", f"Nucleotide Transformer downstream task {t}.", SIDS,
                        {"population": f"{tr} training and {te} test sequences, maximum length {ln} bp; human",
                         "split": "Tenfold cross-validation on the training set; test set as in Supplementary Table 5", "species": "Homo sapiens",
                         "source_locator": "Supplementary Table 5", "missing_metadata": {"version": {"reason": "unreported"}},
                         **({"scope_note": "Supplementary Table 5 prints Promoter TATA as 30000 train / 1372 test and Promoter non-TATA as 5062 / 212; in the public dataset the TATA set is the small one, so the two rows may be swapped in the print. Recorded as printed."} if t in ("Promoter TATA", "Promoter non-TATA") else {})})
    for mode, label in (("probing", "probing"), ("fine-tuning", "fine-tuning (PEFT)")):
        protos[(t, mode)] = b.entity("protocol", b.rid("protocol", t, mode), f"NT benchmark {t}, {label}", f"NT benchmark task {t} under {label}.", SIDS,
            {"protocol": f"{label}; MCC per fold, reported as the median of 10 cross-validation folds with standard deviation. BPNet models are fully trained CNNs and the Raw Probe uses probing in both tables.",
             "version": "Nature Methods 2025", "metric": "matthews-correlation-coefficient", "metric_direction": "higher", "unit": "unitless",
             "limitations": ["Developer benchmark: NT authors ran every model.", "Cross-validation median; the dataset 'test' column of Supplementary Table 5 is not separately reported."],
             "source_locator": "Supplementary Table 6 (probing) or 7 (fine-tuning) caption; Supplementary Table 5"},
            links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": datas[t]}])
agg_data = b.entity("dataset", b.rid("data", "all-18-tasks"), "NT benchmark, all 18 tasks", "All 18 Nucleotide Transformer downstream tasks.", SIDS,
                    {"population": "18 human tasks in three categories: chromatin profiles, regulatory elements, splicing", "split": "Tenfold cross-validation",
                     "source_locator": "Supplementary Table 9 caption", "missing_metadata": {"version": {"reason": "unreported"}}},
                    links=[{"relation": "same_data_as", "target_id": "gfm2-20261011-datta2026-data-nt-benchmark"}])
agg_proto = b.entity("protocol", b.rid("protocol", "normalised-summed-performance"), "NT benchmark normalised summed performance (Supplementary Table 9)",
    "Average of the median MCC over the three task categories.", SIDS,
    {"protocol": "Average of the median MCC obtained by each model on the three categories of downstream tasks (chromatin profiles, regulatory elements, splicing).",
     "version": "Nature Methods 2025", "metric": "matthews-correlation-coefficient", "metric_direction": "higher", "unit": "unitless",
     "limitations": ["Aggregate computed by the authors; per-category values are not printed in this table."], "source_locator": "Supplementary Table 9"},
    links=[{"relation": "part_of", "target_id": BENCH}, {"relation": "uses_data", "target_id": agg_data}])

FAM = {"NT-v1": "discovery-model-nucleotide-transformer", "NT-v2": "catalog-model-nt-v2", "DNABERT-2": "discovery-model-dnabert-2",
       "Enformer": "regulatory-variant-20261009-model-enformer", "HyenaDNA": "regulatory-variant-20261009-model-hyenadna",
       # DNABERT (v1) family record is created in the GFMBench batch, which must be added first.
       "DNABERT-1": "lit-genomics-20261011-gfmbench-model-dnabert"}
new = {}
def family(label):
    if label.startswith("NT-Multispecies-v2"):
        return FAM["NT-v2"]
    if label.startswith("NT"):
        return FAM["NT-v1"]
    for k in ("DNABERT-2", "Enformer", "HyenaDNA", "DNABERT-1"):
        if label.startswith(k):
            return FAM[k]
    name, kind, desc, mt = ({"BPNet": ("BPNet", "model", "BPNet convolutional architecture trained from scratch per task.", ["supervised_machine_learning"]),
                             "Raw Probe": ("Raw sequence probe", "method", "Probe trained on raw one-hot sequence rather than model embeddings (NT benchmark control).", ["conventional_pipeline"])}
                            [label.split(" (")[0] if label.startswith("BPNet") else label])
    if name not in new:
        attrs = {"reported_name": label.split(" (")[0], "entity_level": "family" if kind == "model" else "method", "source_locator": "Supplementary Tables 6, 7 and 9",
                 "missing_metadata": {"version": {"reason": "inapplicable", "note": "Family record; variants are on configurations"}}}
        new[name] = b.entity(kind, b.rid(kind, name), name, desc, SIDS, attrs, method_types=mt)
    return new[name]

cfgs = {}
def config(label, mode):
    approach = {"probing": "probing", "fine-tuning": "parameter-efficient fine-tuning"}[mode]
    if label == "DNABERT-1":
        approach = "fine-tuning"
    if label.startswith("BPNet") or "Randomly Initialized" in label:
        approach = "trained from scratch"
    if label == "Raw Probe":
        approach = "probing of raw sequence"
    key = (label, approach)
    if key not in cfgs:
        fm = not (label.startswith("BPNet") or label == "Raw Probe" or label.startswith("Enformer") or "Randomly" in label)
        cfgs[key] = b.entity("configuration", b.rid("config", label, approach), f"{label}, {approach} (NT benchmark)", f"{label} as evaluated in the NT benchmark, {approach}.", SIDS,
            {"reported_name": label, "foundation_model_eligible": fm, "parameters": f"{approach}; hyperparameters in Supplementary Tables 1 and 8",
             "access_reuse": "Public weights (Hugging Face InstaDeepAI collection)" if label.startswith("NT") and "Randomly" not in label else "Not stated in the tables",
             "source_locator": "Supplementary Tables 6, 7 and 9 row labels",
             **({"limitations": ["Supplementary Table 9 says only 'Finetuning' for DNABERT-1; whether parameter-efficient fine-tuning was used is not stated, and DNABERT-1 has no per-task row in Supplementary Table 7."]} if label == "DNABERT-1" else {}),
             **({"model_identity_note": "Randomly initialised NT architecture trained from scratch; a control, not a pretrained checkpoint"} if "Randomly" in label else {}),
             "missing_metadata": {"version": {"reason": "unreported", "note": "Row label gives training data and parameter count only"}}},
            method_types=["foundation_model"] if fm else ["supervised_machine_learning"], links=[{"relation": "configuration_of", "target_id": family(label)}])
    return cfgs[key]

def origin(label):
    # NT models, NT random-init controls and the Raw Probe are InstaDeep's; BPNet (Avsec et al.) is not.
    return "author_reported" if (label.startswith("NT") or label == "Raw Probe") else "independent_paper"

CELL = r"(\d+(?:\.\d+)?) \(± (\d+(?:\.\d+)?)\)"
# Raw Probe and the three BPNet rows are printed identically in Supplementary Tables 6 and 7 (the
# Table 7 caption says BPNet is fully trained and the Raw Probe uses probing); they are recorded once, from Table 6.
REPEATED = {"Raw Probe", "BPNet (original)", "BPNet (large)", "BPNet (X-large)"}
def parse_table(start, end, table, mode, expected_models):
    seg = lines[start:end]
    blocks, cur_cols = [], None
    for l in seg:
        if l.strip().startswith("Dataset"):
            cur_cols = re.split(r"\s{2,}", l.strip())[1:]
            assert len(cur_cols) == 6, cur_cols
            blocks.append((cur_cols, []))
            continue
        m = re.match(r"^\s*(\S.*?)\s{2,}" + r"\s+".join([CELL] * 6) + r"\s*$", l)
        if m and blocks:
            vals = [(m.group(2 + 2 * i), m.group(3 + 2 * i)) for i in range(6)]
            blocks[-1][1].append((m.group(1).strip(), vals))
    assert len(blocks) == 3, len(blocks)
    assert [c for cols, _ in blocks for c in cols] == TASKS, [c for cols, _ in blocks for c in cols]
    n = 0
    for cols, rows in blocks:
        assert [r[0] for r in rows] == expected_models, [r[0] for r in rows]
        for label, vals in rows:
            if mode == "fine-tuning" and label in REPEATED:
                continue
            c = config(label, mode)
            approach = next(k[1] for k in cfgs if k[0] == label and cfgs[k] == c)
            for t, (v, sd) in zip(cols, vals):
                p, d = protos[(t, mode)], datas[t]
                ev = b.evaluation(b.rid("eval", label, mode, t), f"{label} on NT benchmark {t} ({mode})", SIDS, c, p, d, origin(label),
                    {"protocol_id": p, "dataset_version": None, "split": "Tenfold cross-validation", "population": None, "inputs": f"Human DNA sequence up to {META[t][2]} bp",
                     "adaptation": approach, "metric_implementation": "MCC", "aggregation": "Median over 10 folds", "budget": None},
                    f"{table}, row '{label}', column '{t}'")
                loc = f"{table}, row '{label}', column '{t}'" + ("; printed identically in Supplementary Table 7" if label in REPEATED else "")
                b.result(b.rid("result", label, mode, t), f"{label} {t} {mode} MCC", SRC, SIDS, ev, f"{v} (± {sd})", "matthews-correlation-coefficient", "higher", "unitless",
                         loc, REV(loc), qualifier="median over 10 cross-validation folds", numeric=v,
                         uncertainty={"type": "standard_deviation", "value": sd, "printed": f"± {sd}", "scope": "across 10 cross-validation folds", "n": 10})
                n += 1
    return n

i5 = next(i for i, l in enumerate(lines) if "Supplementary Table 5: Nucleotide Transformer downstream tasks metadata" in l)
i6 = next(i for i, l in enumerate(lines) if "Supplementary Table 6: Downstream performance per task" in l)
i7 = next(i for i, l in enumerate(lines) if "Supplementary Table 7: Downstream performance per task" in l)
i8 = next(i for i, l in enumerate(lines) if "Supplementary Table 8: Hyperparameters" in l)
i9 = next(i for i, l in enumerate(lines) if "Supplementary Table 9: Normalized summed" in l)
probing = ["Raw Probe", "BPNet (original)", "BPNet (large)", "BPNet (X-large)", "NT-HumanRef (500M)", "NT-1000G (500M)", "NT-1000G (2.5B)", "NT-Multispecies (2.5B)"]
finetune = ["Raw Probe", "BPNet (original)", "BPNet (large)", "BPNet (X-large)", "DNABERT-2", "Enformer", "HyenaDNA-1KB", "HyenaDNA-32KB",
            "NT 500M Randomly Initialized", "NT 2.5B Randomly Initialized", "NT-HumanRef (500M)", "NT-1000G (500M)", "NT-1000G (2.5B)", "NT-Multispecies (2.5B)",
            "NT-Multispecies-v2 (50M)", "NT-Multispecies-v2 (100M)", "NT-Multispecies-v2 (250M)", "NT-Multispecies-v2 (500M)"]
n6 = parse_table(i5, i6, "Supplementary Table 6", "probing", probing)
n7 = parse_table(i6, i7, "Supplementary Table 7", "fine-tuning", finetune)
assert (n6, n7) == (144, 252), (n6, n7)

rows9 = []
for l in lines[i8:i9]:
    m = re.match(r"^\s*(\S.*?)\s{2,}(\S.*?)\s{2,}(Training from scratch|Probing|Finetuning|control)\s{2,}(Self-supervised|Supervised|NA)\s+(\d\.\d{3})\s*$", l)
    if m:
        rows9.append(m.groups())
assert len(rows9) == 23, len(rows9)
for label, mtype, approach, pre, v in rows9:
    mode = "probing" if approach == "Probing" else "fine-tuning"
    c = config(label, mode)
    adapt = next(k[1] for k in cfgs if k[0] == label and cfgs[k] == c)
    ev = b.evaluation(b.rid("eval", label, approach, "summary"), f"{label} ({approach}) NT benchmark normalised summed performance", SIDS, c, agg_proto, agg_data, origin(label),
        {"protocol_id": agg_proto, "dataset_version": None, "split": "Tenfold cross-validation", "population": None, "inputs": "Human DNA sequence",
         "adaptation": adapt, "metric_implementation": "MCC", "aggregation": "Mean over three task categories of median MCC", "budget": None},
        f"Supplementary Table 9, row '{label}' ({approach})")
    loc = f"Supplementary Table 9, row '{label}', approach '{approach}', column 'Average performance'"
    b.result(b.rid("result", label, approach, "summary"), f"{label} ({approach}) average MCC", SRC, SIDS, ev, v, "matthews-correlation-coefficient", "higher", "unitless",
             loc, REV(loc), qualifier="mean over three task categories of median cross-validation MCC")
print(json.dumps(b.write()))
