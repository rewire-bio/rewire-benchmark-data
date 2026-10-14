"""Independent review check for batch gfm-guide-sources-20261014 (issue #138).

Written by the reviewer; does not import or run extract/extract_gfm_guide.py.
Usage: python3 -I check_gfm_guide.py <artifact-dir> <batch.jsonl>

The artifact directory holds fresh downloads under these names:
  evee.pdf fig1c.pdf fig1d.pdf fig1d.py common.py evo2.json hegde.xml nt.xml
  ntv3.pdf hyena.pdf card.md agreadme.md agsupp.pdf alphagenome.xml
Needs pdftotext (poppler). Prints one line per result and claim and exits 1 on any mismatch.
"""
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ART = Path(sys.argv[1])
BATCH = Path(sys.argv[2])
P = "gfm-guide-20261014-"

# Stable artifacts must match the pinned hash. bioRxiv PDFs are stamped per download, so their
# hash is reported, not asserted (see the sources' hash_scope).
PINNED = {
    "fig1c.pdf": "3dd79f2055d965fa486ae6c33193c646bb21db51f1491694111b9c96d148eec6",
    "fig1d.pdf": "b1ec938f98392f1b169798f0d9232337d0635ee909e103745151c0c572578136",
    "fig1d.py": "5c03755c6807fef579e234676d86b9e6a20d675e0d520e656e8a60615331e34d",
    "common.py": "1d477d2e1eb4213591015b26baca654e5ca1ca19ee9a1fd39e5f106fc8e56e2e",
    "evo2.json": "8b50005d8a5e8f37d9e504dec246994bf21a326cfb17dcdd086683db616d2254",
    "hegde.xml": "9ea68b688637b40f0aeced7c905822f6b14c352a3a935c61c407945f3d66ef47",
    "nt.xml": "7c3b78a4f38ef053a08e466222e5662dd9711d91c535512d0b35d459d1fc7249",
    "hyena.pdf": "2f471549352ff571ac55faa80c8da453f9bf1ff5b01b6b87fa893457828e798c",
    "card.md": "273893718e3d9ec1adcd462b52127f5a201217d6c39d1bfd13fd963caa2598f1",
    "agreadme.md": "c715b22c31bd4f69e9b76236de0ab6a26c96fa0f384ad56a2f9d2cb65e262681",
    "agsupp.pdf": "86b2e6a07543e3c201e2e157a3e9c6eb5235ff13eb8a5224f6fcb6fe1808d4c0",
    "alphagenome.xml": "50d10530afd474d85702813bc9c9e5431406515e44f3425d64603fdb647fee13",
}
STAMPED = ["evee.pdf", "ntv3.pdf"]

failures = []


def sha(name):
    return hashlib.sha256((ART / name).read_bytes()).hexdigest()


for name, want in PINNED.items():
    got = sha(name)
    print(f"hash {name}: {'match' if got == want else 'MISMATCH ' + got}")
    if got != want:
        failures.append(name)
for name in STAMPED:
    print(f"hash {name}: {sha(name)} (per-download stamp; not compared)")


def pdf(name, first=None, last=None, layout=True):
    args = ["pdftotext"] + (["-layout"] if layout else []) + (["-f", str(first), "-l", str(last)] if first else []) + [str(ART / name), "-"]
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def flat(text):
    return re.sub(r"\s+", " ", text)


def xml_text(name):
    root = ET.parse(ART / name).getroot()
    return flat(" ".join("".join(e.itertext()) for e in root.iter() if e.tag in ("p", "title", "td", "th")))


def xml_table(name, table_id):
    root = ET.parse(ART / name).getroot()
    for tw in root.iter("table-wrap"):
        if tw.get("id") == table_id:
            return [[flat("".join(c.itertext())).strip() for c in tr] for tr in tw.iter("tr")]
    raise SystemExit(f"table {table_id} not found")


def row_after(text, label):
    """Numbers on the first line starting with label."""
    for line in text.splitlines():
        if line.strip().startswith(label):
            return re.findall(r"\d[\d,]*\.?\d*", line[line.index(label) + len(label):])
    raise SystemExit(f"row {label!r} not found")


expected = {}  # result id suffix -> (printed_value, unit)

# EVEE Figure 1c and 1d: Overall rows from the repository vector PDFs. Column order: Figure 1c
# follows METHOD_GROUPS in _heatmap_common.py with EVE absent (no values), checked against the
# rendered paper figure; Figure 1d follows METHOD_COLS in fig1d_indel_heatmap.py.
fig1c = pdf("fig1c.pdf")
assert "(n=158,616, 27.8%P)" in fig1c
c_cols = ["evo2-covariance", "evo2-mean", "evo2-loss", "cadd-v1-7", "alphamissense", "gpn-msa", "ntv3-cosine", "alphagenome"]
common = (ART / "common.py").read_text()
assert '("Evo2 Covariance", "Evo2 Mean", "Evo2 Loss")' in common and '("GPN-MSA", "NTv3", "AlphaGenome")' in common
assert '"NTv3 cosine dist": "NTv3"' in common and '"NTv3 subref probe"' in common.split("DROP_METHODS")[1].split("\n")[0]
c_vals = row_after(fig1c, "Overall")
assert len(c_vals) == 8, c_vals
for col, v in zip(c_cols, c_vals):
    expected[f"result-evee-deconfounded-{col}"] = (v, "unitless")
missense = row_after(fig1c, "Missense")
assert missense[4] == c_vals[4], "AlphaMissense Overall should equal its Missense cell"

fig1d = pdf("fig1d.pdf")
assert "(n=73,961, 65.1%P)" in fig1d
d_src = (ART / "fig1d.py").read_text()
order = re.findall(r'\("(\w+)",\s+"([^"]+)"\)', d_src.split("METHOD_COLS = (")[1].split(")\n")[0] + ")")
assert [o[0] for o in order] == ["evo2_cov_probe_zeroshot", "evo2_mean_probe_supervised", "cadd_v17_indel", "ntv3_subref_probe_supervised"], order
d_vals = row_after(fig1d, "Overall")
for col, v in zip(["evo2-covariance", "evo2-mean", "cadd-v1-7", "ntv3-subref-probe"], d_vals):
    expected[f"result-evee-indel-{col}"] = (v, "unitless")

evee = flat(re.sub(r"\n\d{1,4} ", "\n", pdf("evee.pdf", layout=False)))
assert "Extraction used ∼20,000 H100-hours" in evee
assert "overall AUROC 0.991 vs. 0.980" in evee
expected["result-evee-embedding-extraction-h100-hours"] = ("∼20,000", "hour")

# Hegde et al. 2025: Table A1 and Methods paragraph 3.
a1 = xml_table("hegde.xml", "genes-16-01358-t0A1")
assert a1[0][:3] == ["Seed", "Training Time (Hours)", "Evaluation Time (Minutes)"], a1[0]
for row in a1[1:]:
    expected[f"result-hegde-nt-5-epochs-training-time-seed-{row[0]}"] = (row[1], "hour")
    expected[f"result-hegde-nt-5-epochs-evaluation-time-seed-{row[0]}"] = (row[2], "minute")
hegde = xml_text("hegde.xml")
assert "2 × Quadro RTX 8000 GPUs, taking around 1 h per pruned model on average" in hegde
assert "training to convergence on 2 × NVIDIA TITAN Xp GPUs took approximately 19 h" in hegde
expected["result-hegde-dnabert-2-pruned-convergence-time"] = ("around 1", "hour")
expected["result-hegde-nt-convergence-time"] = ("approximately 19", "hour")

# NTv3 Table 5 (page 34).
t5 = pdf("ntv3.pdf", 34, 34)
assert "Table 5 | H100 GPU-hours required for all training stages" in t5
stages = ["pre-training-8-kb", "length-ext-1-4", "length-ext-5-7", "post-training-1", "post-training-2"]
for size in ["8M", "100M", "650M"]:
    cells = re.findall(r"[\d,]+|NA", t5.split("\n     " + size)[1].split("\n")[0])
    assert len(cells) == 5, (size, cells)
    for stage, v in zip(stages, cells):
        if v != "NA":
            expected[f"result-ntv3-{size.lower()}-{stage}-gpu-hours"] = (v, "hour")

# Nucleotide Transformer, Methods 'Hardware'.
nt = xml_text("nt.xml")
assert "On average, a fine-tuning run lasted 20 min for the 500M-parameter models and 50 min for the 2.5B-parameter models." in nt
expected["result-nt-500m-ia3-fine-tuning-runtime"] = ("20", "minute")
expected["result-nt-2-5b-ia3-fine-tuning-runtime"] = ("50", "minute")

# HyenaDNA Table A.2 (page 17).
a2 = pdf("hyena.pdf", 17, 17)
assert "Table A.2: Pretraining GPU & runtime comparison for short-range models." in a2
assert re.search(r"Params\s+110M\s+2\.5B\s+436K\s+1\.6M", a2)
assert re.search(r"GPUs\s+8-2080 TI\s+128-A100-80GB\s+1-A100-40GB\s+1-A100-40GB", a2)
wall = re.search(r"Wall clock\s+(\d+) days\s+(\d+) days\s+(\d+) mins\s+(\d+) mins", a2).groups()
hrs = row_after(a2, "GPU-hrs")
for i, (m, wu) in enumerate([("dnabert-110m", "day"), ("nt-2-5b", "day"), ("hyenadna-436k", "minute"), ("hyenadna-1-6m", "minute")]):
    expected[f"result-hyenadna-table-a2-{m}-wall-clock"] = (wall[i], wu)
    expected[f"result-hyenadna-table-a2-{m}-gpu-hours"] = (hrs[i], "hour")

# Compare every result in the batch.
records = [json.loads(line) for line in BATCH.read_text().splitlines()]
results = {r["id"].removeprefix(P): r for r in records if r["kind"] == "result" and not r["id"].startswith(P + "result-correction")}
for rid in sorted(set(results) | set(expected)):
    if rid not in results or rid not in expected:
        print(f"result {rid}: MISSING in {'batch' if rid not in results else 'source parse'}")
        failures.append(rid)
        continue
    a = results[rid]["attributes"]
    want_pv, want_unit = expected[rid]
    numeric = re.sub(r"[^\d.]", "", want_pv.replace(",", ""))
    ok = a["printed_value"] == want_pv and float(a["numeric_value"]) == float(numeric) and a["unit"] == want_unit
    print(f"result {rid}: {'match' if ok else 'MISMATCH'} printed={a['printed_value']!r} numeric={a['numeric_value']} unit={a['unit']} source={want_pv!r}/{want_unit}")
    if not ok:
        failures.append(rid)

# Claims: the quoted source text each claim rests on must be present in the artifact.
texts = {
    "agreadme.md": flat((ART / "agreadme.md").read_text()),
    "agsupp.pdf": flat(pdf("agsupp.pdf", 20, 22, layout=False)),
    "alphagenome.xml": xml_text("alphagenome.xml"),
    "card.md": flat((ART / "card.md").read_text()),
    "evee.pdf": evee,
    "evo2.json": json.loads((ART / "evo2.json").read_text())["collection"][0]["authors"],
    "nt.xml": nt,
    "ntv3.pdf": flat(pdf("ntv3.pdf", layout=False)),
}
quotes = {
    "claim-alphagenome-recommended-hardware": [("agreadme.md", "we recommend running with at least an [NVIDIA H100 GPU]"),
        ("agreadme.md", "For training, we recommend running on [Tensor Processing Units (TPUs) v3]"), ("agreadme.md", "or higher."),
        ("agreadme.md", "We strongly recommend using our [AlphaGenome API]"), ("agreadme.md", "without needing specialized hardware")],
    "claim-alphagenome-training-compute": [("agsupp.pdf", "Pre-training utilized TPU v3 hardware, employing sequence parallelism to distribute the computation for each 1 Mb input interval across 8 TPU cores"),
        ("agsupp.pdf", "Each gradient step processed a batch size of 64 samples using 8-way sequence parallelism, requiring 512 TPUv3 cores, with pre-training runs typically completing in approximately 4 hours. Training proceeded for a fixed duration of 15,000 steps"),
        ("agsupp.pdf", "Distillation training was performed without sequence parallelism across 64 NVIDIA H100 GPUs, with a batch size of 64 (effectively one sample per GPU)"),
        ("agsupp.pdf", "The distillation process ran for 250,000 steps, taking approximately 3 days")],
    "claim-alphagenome-variant-scoring-time": [("alphagenome.xml", "making predictions across all modelled modalities and cell types with a single device call per variant. Taking less than 1 s on an NVIDIA H100 GPU, the student model is highly efficient")],
    "claim-evee-developer-overlap": [("evee.pdf", "M.T.P., T.D., R.Y., M.B., D.H., C.F., N.N., M.A., A.J., D.B., and N.K.W. are employees of Goodfire"),
        ("evo2.json", "Nguyen, N."), ("evo2.json", "Balsam, D."), ("evo2.json", "Wang, N. K.")],
    "claim-hyenadna-suggested-gpus": [("card.md", "(T4, T4, T4)"), ("card.md", "(A100-40, T4, T4)"), ("card.md", "(A100-40, A100-40, T4)"),
        ("card.md", "(A100-80, A100-80, A100-40)"), ("card.md", "T4: 16GB A100-40: 40GB A100-80: 80GB"),
        ("card.md", "do inference on DNA sequences up to 450k on the free tier (T4 GPU), and up to 1 million on the paid tier (A100)")],
    "claim-nt-fine-tuning-single-gpu": [("nt.xml", "this fine-tuning approach only requires 0.1% of the total number of parameters, allowing even our largest models to be fine-tuned in under 15 min on a single GPU")],
    "claim-nt-training-compute": [("nt.xml", "using 16 nodes, each equipped with eight A100 GPUs, leading to a total of 128 A100 GPUs used"),
        ("nt.xml", "The 500M-parameter models were trained on a single node for a day, whereas the 2.5B-parameter models required the whole cluster for 28 days to be trained. The NT-v2 models with varying number of parameters ranging from 50 million to 500 million were similarly trained on a single node for a single day."),
        ("nt.xml", "computed and stored on a single node with eight A100 GPUs, requiring 2 days to compute. Then, 760,000 downstream models were fit on a cluster of 3,000 CPUs, requiring 2.5 days")],
    "claim-ntv3-650m-pretraining-wall-clock": [("ntv3.pdf", "processing the full 10.5 trillion tokens required over nine months of H100 GPU-hours. By leveraging a 4-node (32 GPU) setup, the end-to-end wall-clock time was reduced to just under nine days"),
        ("ntv3.pdf", "approximately 3.5M tokens/sec for the 650M model, 7.8M tokens/sec for the 100M model, and 14.5M tokens/sec for the 8M model")],
    "claim-ntv3-inference-hardware": [("ntv3.pdf", "even the largest NTv3 model is designed to run"), ("ntv3.pdf", "inference for full megabase windows on a single A100/H100 GPU"),
        ("ntv3.pdf", "In mixed precision, NTv3 8M can run inference for sequences of several tens of kilobases on a laptop CPU within seconds")],
}
for cid, items in quotes.items():
    missing = [q for f, q in items if q not in texts[f]]
    print(f"claim {cid}: {'match' if not missing else 'MISSING ' + repr(missing)}")
    if missing:
        failures.append(cid)

# Goodfire authors on the EVEE title page: 11 of 23 (affiliation 1).
authors = re.findall(r"([A-Z][\w.]*(?: [A-Z]\.)? [A-Z][\w-]+)\*? ?(\d(?:,\d)*)", flat(pdf("evee.pdf", 1, 1)).split("Goodfire;")[0])
goodfire = [a for a, aff in authors if aff.split(",")[0] == "1"]
print(f"EVEE authors parsed: {len(authors)}, Goodfire: {len(goodfire)}")

print(f"\n{len(results)} results, {len(quotes)} claims checked; {len(failures)} failures")
sys.exit(1 if failures else 0)
